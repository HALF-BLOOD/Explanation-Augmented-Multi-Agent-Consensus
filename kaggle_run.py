"""Work through the run plan a little at a time, one Kaggle session after another.

Stops when a free quota or the session clock runs out. Results, the sampled
data and the response cache are committed to GitHub with --push, and the next
session carries on from there.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

import yaml

from excre import prompts
from excre.config import load_config, load_dotenv
from excre.data import load_hf, read_jsonl
from excre.embed import build_sim
from excre.llm import ModelUnavailable, build_models
from excre.runner import done_ids, models_needed, run_system
from prepare_data import SEED


def load_items(name, n, out):
    path = os.path.join(out, "data", name + ".jsonl")
    if not os.path.exists(path):
        print(f"preparing {name} ...")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for it in load_hf(name, {}, n, SEED):
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
    return read_jsonl(path)


def result_path(out, dataset, job):
    return os.path.join(out, dataset, job.replace(":", "_") + ".jsonl")


def check_frozen(out, cfg):
    now = {
        "models": [{k: m.get(k) for k in ("name", "base_url", "model",
                                          "max_tokens_override", "extra_payload")}
                   for m in cfg["models"]],
        "excre": cfg["excre"], "imrc": cfg["imrc"], "trust": cfg["trust"],
        "sc": cfg["sc"], "judge": cfg["judge"],
        "prompts": prompts.fingerprint(),
    }
    path = os.path.join(out, "manifest.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            was = json.load(f)["frozen"]
        changed = [k for k in now if was.get(k) != now[k]]
        if changed:
            sys.exit(f"{path}: {', '.join(changed)} changed since this run "
                     f"started, so new results would not be comparable with "
                     f"the old ones. Undo the change, or point `out` in the "
                     f"plan at a new folder to start a fresh run.")
        return
    os.makedirs(out, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "frozen": now}, f, indent=1)


def tally(plan, data):
    counts = {}
    seen = {}
    for stage in plan["stages"]:
        for ds in stage["datasets"]:
            ids = [it["id"] for it in data[ds][:stage["n"]]]
            for job in stage["systems"]:
                path = result_path(plan["out"], ds, job)
                if path not in seen:
                    seen[path] = {}
                    if os.path.exists(path):
                        seen[path] = {r["id"]: bool(r.get("correct"))
                                      for r in read_jsonl(path) if "error" not in r}
                got = [seen[path][i] for i in ids if i in seen[path]]
                counts[stage["name"], ds, job] = (len(got), sum(got), len(ids))
    return counts, sum(len(v) for v in seen.values())


def work(plan, data, models, simfn, cfg, stop_at, benched, tick):
    block = plan.get("block", 10)
    for stage in plan["stages"]:
        finished = {}
        for upto in range(block, stage["n"] + block, block):
            for ds in stage["datasets"]:
                items = data[ds][:min(upto, stage["n"])]
                for job in stage["systems"]:
                    if time.time() > stop_at:
                        return "out of session time"
                    system = job.removesuffix("_adv")
                    if models_needed(system, models) & set(benched):
                        continue
                    path = result_path(plan["out"], ds, job)
                    if path not in finished:
                        finished[path] = done_ids(path)
                    if all(it["id"] in finished[path] for it in items):
                        continue
                    try:
                        run_system(system, items, models, simfn, cfg, path,
                                   adversarial=job.endswith("_adv"),
                                   log=lambda m, ds=ds: print(ds, m, flush=True),
                                   stop_at=stop_at, after_item=tick)
                    except ModelUnavailable as e:
                        print(f"!! {e.model} benched for this session: {e.why}")
                        benched[e.model] = e.why
                    finished[path] = done_ids(path)
            # no running ahead on the models that are still up: that would eat
            # tomorrow's quota for the jobs that need all three
            if benched:
                return f"stage '{stage['name']}' waiting on " + ", ".join(benched)
    return None


def write_progress(plan, counts, note):
    lines = [f"# {plan['out']}", "", note, "", "done / total (accuracy so far)"]
    for stage in plan["stages"]:
        head = stage["datasets"]
        lines += ["", f"## {stage['name']}", "",
                  "| system | " + " | ".join(head) + " |",
                  "|---" * (len(head) + 1) + "|"]
        for job in stage["systems"]:
            cells = []
            for ds in head:
                done, right, total = counts[stage["name"], ds, job]
                acc = f" ({100 * right / done:.0f}%)" if done else ""
                cells.append(f"{done}/{total}{acc}")
            lines.append(f"| {job} | " + " | ".join(cells) + " |")
    with open(os.path.join(plan["out"], "progress.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def write_reports(plan, data):
    for ds in data:
        folder = os.path.join(plan["out"], ds)
        if not os.path.isdir(folder):
            continue
        res = subprocess.run([sys.executable, "analyze_results.py", "--results", folder],
                             capture_output=True, text=True)
        with open(os.path.join(folder, "report.txt"), "w", encoding="utf-8") as f:
            f.write(res.stdout if res.returncode == 0 else res.stdout + res.stderr)


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True)


def push(paths, message):
    git("add", *paths)
    if git("diff", "--cached", "--quiet").returncode == 0:
        print("nothing new to commit")
        return
    who = []
    if not git("config", "user.email").stdout.strip():
        who = ["-c", "user.name=kaggle-runner",
               "-c", "user.email=kaggle-runner@users.noreply.github.com"]
    res = git(*who, "commit", "-q", "-m", message)
    if res.returncode:
        print("commit failed:", res.stderr.strip())
        return
    branch = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    for _ in range(3):
        if git("pull", "-q", "--rebase", "--autostash", "origin", branch).returncode:
            git("rebase", "--abort")
        res = git("push", "-q", "origin", "HEAD")
        if res.returncode == 0:
            print(f"pushed: {message}")
            return
        print("push failed:", res.stderr.strip()[:300])
        time.sleep(10)
    print("giving up on the push, the commit is still in this clone")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default=os.path.join("configs", "kaggle_plan.yaml"))
    ap.add_argument("--hours", type=float, default=11.0,
                    help="wrap up after this long (kaggle kills sessions at 12h)")
    ap.add_argument("--push", action="store_true", help="commit + push results")
    ap.add_argument("--push-every", type=float, default=30, help="minutes")
    args = ap.parse_args()

    load_dotenv()
    with open(args.plan, encoding="utf-8") as f:
        plan = yaml.safe_load(f)
    out = plan["out"]
    cfg = load_config(plan["config"])
    cfg["cache_dir"] = plan.get("cache", os.path.join(out, "cache"))
    check_frozen(out, cfg)
    models = build_models(cfg["models"], cache_dir=cfg["cache_dir"], use_cache=True)
    simfn = build_sim(cfg["imrc"])

    sizes = {}
    for stage in plan["stages"]:
        for ds in stage["datasets"]:
            sizes[ds] = max(sizes.get(ds, 300), stage["n"])
    data = {ds: load_items(ds, n, out) for ds, n in sizes.items()}
    tracked = [out, cfg["cache_dir"]]

    start = time.time()
    began = datetime.now(timezone.utc)
    before = tally(plan, data)[1]
    benched = {}
    last_push = start

    def snapshot(stopped=None):
        counts, total = tally(plan, data)
        added = total - before
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        note = f"updated {stamp}, +{added} this session"
        if stopped:
            note += f", stopped: {stopped}"
        for m, why in benched.items():
            note += f"  \n{m} benched: {why[:150]}"
        write_progress(plan, counts, note)
        return added, stamp

    def tick():
        nonlocal last_push
        if args.push and time.time() - last_push > args.push_every * 60:
            added, stamp = snapshot()
            push(tracked, f"checkpoint {stamp} (+{added})")
            last_push = time.time()

    print(f"plan {args.plan}: {before} records already done, "
          f"models {', '.join(m.name for m in models)}")
    try:
        stopped = work(plan, data, models, simfn, cfg,
                       start + args.hours * 3600, benched, tick)
    except KeyboardInterrupt:
        stopped = "interrupted"
    if stopped is None:
        left = sum(c[2] - c[0] for c in tally(plan, data)[0].values())
        stopped = "plan finished" if left == 0 else f"{left} records still failing"

    added, stamp = snapshot(stopped)
    write_reports(plan, data)
    with open(os.path.join(out, "sessions.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "start": began.isoformat(timespec="seconds"),
            "hours": round((time.time() - start) / 3600, 2),
            "added": added, "stopped": stopped, "benched": benched,
            "where": os.environ.get("KAGGLE_KERNEL_RUN_TYPE", "local"),
        }) + "\n")
    print(f"\n{stopped}. +{added} records this session, see {out}/progress.md")
    if args.push:
        push(tracked, f"run {stamp}: +{added}, {stopped}")


if __name__ == "__main__":
    main()

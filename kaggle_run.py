"""Work through the run plan a little at a time, one Kaggle session after another.

Stops when the free quotas or the session clock run out. Results, the sampled
data and the response cache all sit under the plan's `out` folder; with --push
that folder is committed to GitHub and the next session carries on from it.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

import yaml

from excre.config import load_config, load_dotenv
from excre.data import load_hf, read_jsonl
from excre.embed import build_sim
from excre.llm import ModelUnavailable, build_models
from excre.runner import models_needed, run_system
from prepare_data import SEED


def load_items(name, n, out):
    path = os.path.join(out, "data", name + ".jsonl")
    if not os.path.exists(path):
        print(f"preparing {name} ...")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for it in load_hf(name, {}, n, SEED):
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
    return read_jsonl(path)[:n]


def result_path(out, dataset, job):
    return os.path.join(out, dataset, job.replace(":", "_") + ".jsonl")


def tally(plan, data):
    counts = {}
    for ds, items in data.items():
        ids = {it["id"] for it in items}
        for job in plan["systems"]:
            path = result_path(plan["out"], ds, job)
            recs = {}
            if os.path.exists(path):
                recs = {r["id"]: r for r in read_jsonl(path)
                        if "error" not in r and r["id"] in ids}
            right = sum(bool(r.get("correct")) for r in recs.values())
            counts[ds, job] = (len(recs), right, len(items))
    return counts


def work(plan, data, models, simfn, cfg, stop_at, benched, tick):
    names = {m.name for m in models}
    block = plan.get("block", 10)
    for upto in range(block, plan["n"] + block, block):
        for ds, items in data.items():
            for job in plan["systems"]:
                if time.time() > stop_at:
                    return "out of session time"
                if names <= set(benched):
                    return "every model is out of quota"
                system = job.removesuffix("_adv")
                if models_needed(system, models) & set(benched):
                    continue
                try:
                    run_system(system, items[:upto], models, simfn, cfg,
                               result_path(plan["out"], ds, job),
                               adversarial=job.endswith("_adv"),
                               log=lambda m, ds=ds: print(ds, m, flush=True),
                               stop_at=stop_at, after_item=tick)
                except ModelUnavailable as e:
                    print(f"!! {e.model} benched for this session: {e.why}")
                    benched[e.model] = e.why
    return None


def write_progress(plan, counts, note):
    head = plan["datasets"]
    lines = [f"# {plan['out']}", "", note, "",
             "done / total (accuracy so far)", "",
             "| system | " + " | ".join(head) + " |",
             "|---" * (len(head) + 1) + "|"]
    for job in plan["systems"]:
        cells = []
        for ds in head:
            done, right, total = counts[ds, job]
            acc = f" ({100 * right / done:.0f}%)" if done else ""
            cells.append(f"{done}/{total}{acc}")
        lines.append(f"| {job} | " + " | ".join(cells) + " |")
    with open(os.path.join(plan["out"], "progress.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def write_reports(plan):
    for ds in plan["datasets"]:
        folder = os.path.join(plan["out"], ds)
        if not os.path.isdir(folder):
            continue
        res = subprocess.run([sys.executable, "analyze_results.py", "--results", folder],
                             capture_output=True, text=True)
        with open(os.path.join(folder, "report.txt"), "w", encoding="utf-8") as f:
            f.write(res.stdout if res.returncode == 0 else res.stdout + res.stderr)


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True)


def push(out, message):
    git("add", out)
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
    cfg["cache_dir"] = os.path.join(out, "cache")
    models = build_models(cfg["models"], cache_dir=cfg["cache_dir"], use_cache=True)
    simfn = build_sim(cfg["imrc"])
    data = {ds: load_items(ds, plan["n"], out) for ds in plan["datasets"]}

    start = time.time()
    began = datetime.now(timezone.utc)
    before = sum(c[0] for c in tally(plan, data).values())
    benched = {}
    last_push = start

    def snapshot(stopped=None):
        counts = tally(plan, data)
        added = sum(c[0] for c in counts.values()) - before
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        note = f"updated {stamp}, +{added} this session"
        if stopped:
            note += f", stopped: {stopped}"
        for m, why in benched.items():
            note += f"  \n{m} benched: {why[:150]}"
        write_progress(plan, counts, note)
        return counts, added, stamp

    def tick():
        nonlocal last_push
        if args.push and time.time() - last_push > args.push_every * 60:
            _, added, stamp = snapshot()
            push(out, f"checkpoint {stamp} (+{added})")
            last_push = time.time()

    print(f"plan {args.plan}: {before} records already done, "
          f"models {', '.join(m.name for m in models)}")
    try:
        stopped = work(plan, data, models, simfn, cfg,
                       start + args.hours * 3600, benched, tick)
    except KeyboardInterrupt:
        stopped = "interrupted"
    if stopped is None:
        left = sum(c[2] - c[0] for c in tally(plan, data).values())
        stopped = "plan finished" if left == 0 else \
            f"{left} left but nothing runnable with the models still up"

    _, added, stamp = snapshot(stopped)
    write_reports(plan)
    with open(os.path.join(out, "sessions.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "start": began.isoformat(timespec="seconds"),
            "hours": round((time.time() - start) / 3600, 2),
            "added": added, "stopped": stopped, "benched": benched,
            "where": os.environ.get("KAGGLE_KERNEL_RUN_TYPE", "local"),
        }) + "\n")
    print(f"\n{stopped}. +{added} records this session, see {out}/progress.md")
    if args.push:
        push(out, f"run {stamp}: +{added}, {stopped}")


if __name__ == "__main__":
    main()

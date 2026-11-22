"""Work through the run plan a little at a time, one Kaggle session after another.

The plan is walked one question at a time: question 1 of every dataset goes
through every experiment that uses it, then question 2, and so on, so the
results stay balanced across datasets and experiments whenever the run stops.
A session ends when a free quota or the session clock runs out. Results, the
sampled data and the response cache are committed to GitHub with --push, and
the next session carries on from there.
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
from excre.data import append_jsonl, load_hf, read_jsonl
from excre.embed import build_sim
from excre.llm import ModelUnavailable, build_models, resolve_api_keys
from excre.runner import models_needed, run_item
from prepare_data import SEED

# an item that crashes this many times is left out instead of retried forever
GIVE_UP = 2


def load_items(name, n, out):
    # drawn from hugging face once per run folder and kept there, so every
    # session asks the same questions and the paper can list exactly which.
    # Asking for more than the folder holds redraws at the recorded revision,
    # which keeps the questions already there and adds new ones after them
    folder = os.path.join(out, "data")
    path = os.path.join(folder, name + ".jsonl")
    record = os.path.join(folder, "sources.json")
    have = read_jsonl(path) if os.path.exists(path) else []
    if len(have) >= n:
        return have
    sources = {}
    if os.path.exists(record):
        with open(record, encoding="utf-8") as f:
            sources = json.load(f)
    print(f"drawing {n} {name} questions from hugging face ...")
    items, source = load_hf(name, {}, n, SEED,
                            revision=sources.get(name, {}).get("revision"))
    same = lambda it: (it["question"], it["choices"], it["gold"])
    if [same(it) for it in items[:len(have)]] != [same(it) for it in have]:
        sys.exit(f"{path}: a bigger draw does not start with the questions "
                 f"already in the run, so it was not saved")
    os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    sources[name] = source
    with open(record, "w", encoding="utf-8") as f:
        json.dump(sources, f, indent=1)
    return items


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
        "prompts_stepsfirst": prompts.fingerprint(prompts.SCHEMA_STEPS_FIRST),
    }
    path = os.path.join(out, "manifest.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            manifest = json.load(f)
        was = manifest["frozen"]
        changed = [k for k in now if k in was and was[k] != now[k]]
        if changed:
            sys.exit(f"{path}: {', '.join(changed)} changed since this run "
                     f"started, so new results would not be comparable with "
                     f"the old ones. Undo the change, or point `out` in the "
                     f"plan at a new folder to start a fresh run.")
        # something added after the run started is frozen from its first session
        new = [k for k in now if k not in was]
        if new:
            stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
            was.update({k: now[k] for k in new})
            manifest.setdefault("added", {}).update({k: stamp for k in new})
            with open(path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=1)
        return
    os.makedirs(out, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "frozen": now}, f, indent=1)


def datasets_in(plan):
    return list(dict.fromkeys(ds for s in plan["stages"] for ds in s["datasets"]))


def depth(plan, ds):
    return max(s["n"] for s in plan["stages"] if ds in s["datasets"])


def jobs_at(plan, ds, i):
    jobs = []
    for stage in plan["stages"]:
        if ds in stage["datasets"] and i < stage["n"]:
            jobs += [j for j in stage["systems"] if j not in jobs]
    return jobs


def entry(book, out, ds, job):
    # each results file is read once per session and kept up to date in memory
    path = result_path(out, ds, job)
    if path not in book:
        done, errors = {}, {}
        if os.path.exists(path):
            for r in read_jsonl(path):
                if "error" in r:
                    errors[r["id"]] = errors.get(r["id"], 0) + 1
                else:
                    done[r["id"]] = bool(r.get("correct"))
        book[path] = (done, errors)
    return (path, *book[path])


def settled(book, out, ds, job, item_id):
    _, done, errors = entry(book, out, ds, job)
    return item_id in done or errors.get(item_id, 0) >= GIVE_UP


def tally(plan, data, book):
    out = plan["out"]
    counts = {}
    for stage in plan["stages"]:
        for ds in stage["datasets"]:
            ids = [it["id"] for it in data[ds][:stage["n"]]]
            for job in stage["systems"]:
                _, done, _ = entry(book, out, ds, job)
                got = [done[i] for i in ids if i in done]
                counts[stage["name"], ds, job] = (len(got), sum(got), len(ids))
    rows = {}
    for ds in datasets_in(plan):
        i = 0
        while i < depth(plan, ds) and all(
                settled(book, out, ds, job, data[ds][i]["id"])
                for job in jobs_at(plan, ds, i)):
            i += 1
        rows[ds] = i
    return counts, rows


def records(book):
    return sum(len(done) for done, _ in book.values())


def work(plan, data, models, simfn, cfg, book, stop_at, benched, tick):
    out = plan["out"]
    order = datasets_in(plan)
    for i in range(max(depth(plan, ds) for ds in order)):
        for ds in order:
            if i >= depth(plan, ds):
                continue
            item = data[ds][i]
            for job in jobs_at(plan, ds, i):
                if time.time() > stop_at:
                    return "out of session time"
                system = job.removesuffix("_adv")
                if models_needed(system, models) & set(benched):
                    continue
                if settled(book, out, ds, job, item["id"]):
                    continue
                path, done, errors = entry(book, out, ds, job)
                t0 = time.time()
                try:
                    rec = run_item(system, i, item, models, simfn, cfg,
                                   adversarial=job.endswith("_adv"))
                except ModelUnavailable as e:
                    print(f"!! {e.model} benched for this session: {e.why}",
                          flush=True)
                    benched[e.model] = e.why
                    continue
                append_jsonl(path, rec)
                if "error" in rec:
                    errors[item["id"]] = errors.get(item["id"], 0) + 1
                    what = "error: " + rec["error"].strip().splitlines()[-1][:120]
                else:
                    done[item["id"]] = rec["correct"]
                    what = "right" if rec["correct"] else "wrong"
                print(f"{item['id']:<16} {job:<24} {what} "
                      f"({time.time() - t0:.0f}s)", flush=True)
                tick()
        # no running ahead on the models that are still up: that would eat
        # tomorrow's quota for the jobs that need all three
        if benched:
            return f"question {i + 1} waiting on " + ", ".join(benched)
    return None


def write_progress(plan, data, book, note):
    counts, rows = tally(plan, data, book)
    order = datasets_in(plan)
    lines = [f"# {plan['out']}", "", note, "",
             "questions finished by every system that runs them",
             "", "| " + " | ".join(order) + " |", "|---" * len(order) + "|",
             "| " + " | ".join(f"{rows[ds]}/{depth(plan, ds)}" for ds in order) + " |",
             "", "done / total (accuracy so far)"]
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
    return rows


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

    data = {ds: load_items(ds, max(300, depth(plan, ds)), out)
            for ds in datasets_in(plan)}
    tracked = [out, cfg["cache_dir"]]

    start = time.time()
    began = datetime.now(timezone.utc)
    book = {}
    rows = tally(plan, data, book)[1]
    before = records(book)
    benched = {}
    last_push = start

    def snapshot(stopped=None):
        added = records(book) - before
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        note = f"updated {stamp}, +{added} this session"
        if stopped:
            note += f", stopped: {stopped}"
        for m, why in benched.items():
            note += f"  \n{m} benched: {why[:150]}"
        return added, stamp, write_progress(plan, data, book, note)

    def tick():
        nonlocal last_push
        if args.push and time.time() - last_push > args.push_every * 60:
            added, stamp, _ = snapshot()
            push(tracked, f"checkpoint {stamp} (+{added})")
            last_push = time.time()

    def m_label(m):
        if hasattr(m, "api_key_env"):
            nk = len(resolve_api_keys(m.api_key_env))
            return f"{m.name} ({nk} key{'s' if nk != 1 else ''})"
        return m.name

    print(f"plan {args.plan}: {before} records already done, "
          f"models: {', '.join(m_label(m) for m in models)}")
    print("questions done: " + ", ".join(
        f"{ds} {n}/{depth(plan, ds)}" for ds, n in rows.items()), flush=True)
    try:
        stopped = work(plan, data, models, simfn, cfg, book,
                       start + args.hours * 3600, benched, tick)
    except KeyboardInterrupt:
        stopped = "interrupted"
    if stopped is None:
        rows = tally(plan, data, book)[1]
        short = [ds for ds, n in rows.items() if n < depth(plan, ds)]
        stopped = ("plan finished" if not short else
                   "a few items failed and get one more try next session")

    added, stamp, rows = snapshot(stopped)
    write_reports(plan, data)
    with open(os.path.join(out, "sessions.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "start": began.isoformat(timespec="seconds"),
            "hours": round((time.time() - start) / 3600, 2),
            "added": added, "stopped": stopped, "benched": benched,
            "questions": rows,
            "where": os.environ.get("KAGGLE_KERNEL_RUN_TYPE", "local"),
        }) + "\n")
    print(f"\n{stopped}. +{added} records this session, see {out}/progress.md")
    if args.push:
        push(tracked, f"run {stamp}: +{added}, {stopped}")


if __name__ == "__main__":
    main()

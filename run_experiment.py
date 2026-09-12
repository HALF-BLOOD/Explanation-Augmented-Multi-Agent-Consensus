"""CLI runner for evaluation across benchmark datasets and reasoning systems."""

import argparse
import os

from excre.config import load_config, load_dotenv
from excre.data import read_jsonl
from excre.embed import build_sim
from excre.llm import build_models
from excre.runner import run_system

DEFAULT_DATA = os.path.join("data", "samples", "dev_numeric.jsonl")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join("configs", "default.yaml"))
    ap.add_argument("--data", default=DEFAULT_DATA)
    ap.add_argument("--n", type=int, default=0, help="cap items (0 = all)")
    ap.add_argument("--systems", default="excre,cot,sc,mad",
                    help="comma list: excre, cot[:model], sc[:model], mad, "
                         "reconcile, judge")
    ap.add_argument("--out", default=os.path.join("results", "dev"))
    ap.add_argument("--rounds", type=int, default=None,
                    help="override excre/mad round count")
    ap.add_argument("--adversarial", action="store_true",
                    help="excre only: plant a rotating saboteur")
    args = ap.parse_args()

    load_dotenv()
    cfg = load_config(args.config)
    if args.rounds is not None:
        cfg["excre"]["rounds"] = args.rounds

    items = read_jsonl(args.data)
    if args.n:
        items = items[: args.n]
    print(f"{len(items)} items from {args.data}")

    models = build_models(cfg["models"], cache_dir=cfg["cache_dir"],
                          use_cache=cfg["cache"])
    print("models:", ", ".join(m.name for m in models))
    simfn = build_sim(cfg["imrc"])

    for system in [s.strip() for s in args.systems.split(",") if s.strip()]:
        suffix = "_adv" if (args.adversarial and system == "excre") else ""
        fname = system.replace(":", "_") + suffix + ".jsonl"
        out_path = os.path.join(args.out, fname)
        run_system(system, items, models, simfn, cfg, out_path,
                   adversarial=(args.adversarial and system == "excre"))


if __name__ == "__main__":
    main()

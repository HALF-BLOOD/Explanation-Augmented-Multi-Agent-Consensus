"""Download benchmark datasets from Hugging Face and format into normalized JSONL."""

import argparse
import json
import os

from excre.data import AVAILABLE_DATASETS, load_hf

SEED = 20049123


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", default="gsm8k",
                    help=f"comma list from: {', '.join(AVAILABLE_DATASETS)}")
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--out", default="data")
    ap.add_argument("--split", default=None,
                    help="override the source split (gsm8k only: use train "
                         "to build a tuning slice disjoint from the test set)")
    ap.add_argument("--suffix", default="",
                    help="filename suffix, e.g. _dev for tuning slices")
    args = ap.parse_args()

    cfg = {"split": args.split} if args.split else {}
    os.makedirs(args.out, exist_ok=True)
    for name in [d.strip() for d in args.datasets.split(",") if d.strip()]:
        if name not in AVAILABLE_DATASETS:
            print(f"skipping unknown dataset: {name}")
            continue
        print(f"fetching {name} ...")
        items = load_hf(name, cfg, args.n, SEED)
        if args.suffix:
            # keep ids distinct from the main file so results can never be
            # paired across the wrong slices
            for i, it in enumerate(items):
                it["id"] = f"{name}{args.suffix}-{i:04d}"
        path = os.path.join(args.out, f"{name}{args.suffix}.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            for it in items:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
        print(f"  wrote {len(items)} items -> {path}")


if __name__ == "__main__":
    main()

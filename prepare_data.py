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
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    for name in [d.strip() for d in args.datasets.split(",") if d.strip()]:
        if name not in AVAILABLE_DATASETS:
            print(f"skipping unknown dataset: {name}")
            continue
        print(f"fetching {name} ...")
        items = load_hf(name, {}, args.n, SEED)
        path = os.path.join(args.out, f"{name}.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            for it in items:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
        print(f"  wrote {len(items)} items -> {path}")


if __name__ == "__main__":
    main()

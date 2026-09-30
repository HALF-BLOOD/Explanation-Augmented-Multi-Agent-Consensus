"""Build the hand-labelling sheet for IMRC validation.

Samples model pairs from an excre results file and writes a CSV where each
row shows two full reasoning paths side by side, with an empty
`congruence_0_to_4` column to fill in by hand (0 = completely different
reasoning, 4 = same reasoning in different words). The IMRC scores are NOT
shown on the sheet, so the labelling stays blind; they are stored in a
separate key file for the correlation check afterwards.

    python make_label_sheet.py --results results/pilot-dev/excre.jsonl \
        --n 60 --out labels/pilot
"""

import argparse
import csv
import json
import os
import random
from itertools import combinations

from excre.config import load_config
from excre.data import read_jsonl
from excre.embed import build_sim
from excre.imrc import imrc_pair


def path_text(path):
    lines = [f"answer: {path['answer']}"]
    for s in path["steps"]:
        ev = f"  [evidence: {s['evidence']}]" if s["evidence"] else ""
        lines.append(f"- {s['claim']}{ev}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--config", default="configs/pilot.yaml")
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--seed", type=int, default=20049123)
    ap.add_argument("--out", default="labels/pilot")
    args = ap.parse_args()

    cfg = load_config(args.config)
    simfn = build_sim(cfg["imrc"])
    w = (cfg["imrc"]["alpha"], cfg["imrc"]["beta"], cfg["imrc"]["gamma"])

    candidates = []
    for rec in read_jsonl(args.results):
        if "error" in rec:
            continue
        last = rec["rounds_run"]
        finals = [(t["model"], t["path"]) for t in rec["trail"]
                  if t["round"] == last and t["path"]["steps"]]
        for (ma, pa), (mb, pb) in combinations(finals, 2):
            candidates.append((rec["id"], ma, mb, pa, pb))

    rng = random.Random(args.seed)
    rng.shuffle(candidates)
    picked = candidates[: args.n]

    os.makedirs(args.out, exist_ok=True)
    sheet = os.path.join(args.out, "label_sheet.csv")
    key = os.path.join(args.out, "imrc_key.jsonl")
    with open(sheet, "w", newline="", encoding="utf-8") as fs, \
         open(key, "w", encoding="utf-8") as fk:
        wr = csv.writer(fs)
        wr.writerow(["pair_id", "path_A", "path_B", "congruence_0_to_4"])
        for k, (item_id, ma, mb, pa, pb) in enumerate(picked):
            pair_id = f"pair-{k:03d}"
            wr.writerow([pair_id, path_text(pa), path_text(pb), ""])
            scores = imrc_pair(pa, pb, simfn, w,
                               cfg["imrc"].get("evidence_threshold", 0.5))
            fk.write(json.dumps({"pair_id": pair_id, "item_id": item_id,
                                 "models": [ma, mb], **scores}) + "\n")
    print(f"wrote {len(picked)} pairs -> {sheet}")
    print(f"blind key (do not open until labelling is done) -> {key}")
    print("label scale: 0 different reasoning ... 4 same reasoning, "
          "then run check_labels.py")


if __name__ == "__main__":
    main()

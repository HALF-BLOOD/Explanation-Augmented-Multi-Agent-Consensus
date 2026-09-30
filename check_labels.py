"""Correlate hand labels with IMRC. Run after filling in label_sheet.csv.

Prints Spearman of each IMRC component (and the composite) against the
human congruence labels -- this is the validation number for the metric
itself, and the component correlations feed the alpha/beta/gamma choice.
"""

import argparse
import csv
import json

from excre.stats import spearman


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="labels/pilot")
    args = ap.parse_args()

    labels = {}
    with open(f"{args.dir}/label_sheet.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            v = row["congruence_0_to_4"].strip()
            if v:
                labels[row["pair_id"]] = float(v)

    keyed = []
    with open(f"{args.dir}/imrc_key.jsonl", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if rec["pair_id"] in labels:
                keyed.append((labels[rec["pair_id"]], rec))

    if len(keyed) < 10:
        print(f"only {len(keyed)} labelled pairs found -- fill in the sheet "
              f"first (needs the congruence_0_to_4 column)")
        return

    human = [h for h, _ in keyed]
    print(f"{len(keyed)} labelled pairs")
    for comp in ("semantic", "structural", "evidence", "imrc"):
        vals = [r[comp] for _, r in keyed]
        print(f"  spearman(human, {comp:<10}) = {spearman(vals, human):+.3f}")


if __name__ == "__main__":
    main()

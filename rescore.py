"""Recompute IMRC / trust / fragility from stored reasoning paths.

The engine writes the full audit trail into every excre result line, so
metric variants (different embedder, different alpha/beta/gamma, different
trust weights) never need fresh API calls -- this is what makes the pilot
grid search affordable. Reads one results file, rewrites the metric fields,
writes a new file; the trail itself is untouched.

    python rescore.py --results results/pilot-dev/excre.jsonl \
        --data data/samples/dev_numeric.jsonl \
        --config configs/pilot.yaml --out results/pilot-dev/excre_sbert.jsonl
"""

import argparse
import json

from excre.config import load_config
from excre.data import make_normaliser, read_jsonl
from excre.embed import build_sim
from excre.imrc import imrc_group
from excre.trust import (coalition, consensus_answer, fragility,
                         trust_components, trust_score)


def final_paths(rec):
    last = rec["rounds_run"]
    return [t["path"] for t in rec["trail"] if t["round"] == last]


def rescore(rec, item, simfn, cfg):
    w = (cfg["imrc"]["alpha"], cfg["imrc"]["beta"], cfg["imrc"]["gamma"])
    thr = cfg["imrc"].get("evidence_threshold", 0.5)
    norm = make_normaliser(item["format"])

    paths = final_paths(rec)
    answer, agreement = consensus_answer(paths, norm)
    coal = coalition(paths, answer, norm)
    imrc_all = imrc_group(paths, simfn, w, thr)
    imrc_coal = imrc_group(coal, simfn, w, thr)
    comps = trust_components(coal, imrc_all["imrc"], imrc_coal["imrc"],
                             agreement, rec.get("converged", False))

    out = dict(rec)
    out["answer"] = answer
    out["correct"] = norm(answer) == norm(item["gold"])
    out["imrc_all"] = imrc_all
    out["imrc_coalition"] = imrc_coal
    out["components"] = comps
    out["trust"] = trust_score(comps, cfg["trust"])
    out["signal"] = out["trust"]
    out["fragility"] = fragility(agreement, imrc_coal["imrc"])
    out["rescored_with"] = {"embedder": simfn.name, "alpha": w[0],
                            "beta": w[1], "gamma": w[2]}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--config", default="configs/pilot.yaml")
    ap.add_argument("--out", required=True)
    # quick overrides so a grid search is a shell loop, not 20 yaml files
    ap.add_argument("--alpha", type=float, default=None)
    ap.add_argument("--beta", type=float, default=None)
    ap.add_argument("--gamma", type=float, default=None)
    ap.add_argument("--embedder", default=None)
    args = ap.parse_args()

    cfg = load_config(args.config)
    for k in ("alpha", "beta", "gamma", "embedder"):
        v = getattr(args, k)
        if v is not None:
            cfg["imrc"][k] = v
    simfn = build_sim(cfg["imrc"])

    items = {it["id"]: it for it in read_jsonl(args.data)}
    recs = read_jsonl(args.results)
    n_out = 0
    with open(args.out, "w", encoding="utf-8") as f:
        for rec in recs:
            if "error" in rec or rec["id"] not in items:
                continue
            out = rescore(rec, items[rec["id"]], simfn, cfg)
            f.write(json.dumps(out, ensure_ascii=False) + "\n")
            n_out += 1
    print(f"rescored {n_out} records -> {args.out} "
          f"(embedder={simfn.name})")


if __name__ == "__main__":
    main()

"""Results evaluation script.

Computes:
- System accuracy with 95% Wilson confidence intervals and average token costs
- Exact McNemar tests with Holm-Bonferroni correction vs baselines
- Spearman rank correlation of confidence/trust gating signals with correctness
- Selective classification risk-coverage curves and AURC metrics
- Paired clean vs adversarial robustness analysis and fragility AUROC
"""

import argparse
import glob
import os
from collections import defaultdict

from excre.data import read_jsonl
from excre.stats import (accuracy_at_coverage, auroc, holm, mcnemar_exact,
                         risk_coverage, spearman, wilson_ci)


def load_dir(path):
    runs = {}
    for f in sorted(glob.glob(os.path.join(path, "*.jsonl"))):
        name = os.path.splitext(os.path.basename(f))[0]
        recs = [r for r in read_jsonl(f) if "error" not in r]
        if recs:
            runs[name] = {r["id"]: r for r in recs}
    return runs


def fmt_pct(x):
    return f"{100 * x:5.1f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join("results", "dev"))
    args = ap.parse_args()

    runs = load_dir(args.results)
    if not runs:
        print(f"nothing readable in {args.results}")
        return

    print(f"\n== accuracy ({args.results}) ==")
    print(f"{'system':<16} {'n':>5} {'acc%':>6} {'95% CI':>15} {'tok/item':>9}")
    for name, recs in runs.items():
        rs = list(recs.values())
        n = len(rs)
        k = sum(1 for r in rs if r.get("correct"))
        p, lo, hi = wilson_ci(k, n)
        toks = [r["tokens"]["prompt"] + r["tokens"]["completion"]
                for r in rs if "tokens" in r]
        tok = sum(toks) / len(toks) if toks else 0
        print(f"{name:<16} {n:>5} {fmt_pct(p):>6} "
              f"[{fmt_pct(lo)},{fmt_pct(hi)}] {tok:>9.0f}")

    if "excre" in runs:
        base_names = [n for n in runs if n not in ("excre", "excre_adv")]
        pvals, rows = [], []
        for bn in base_names:
            common = sorted(set(runs["excre"]) & set(runs[bn]))
            b = sum(1 for i in common
                    if runs["excre"][i].get("correct")
                    and not runs[bn][i].get("correct"))
            c = sum(1 for i in common
                    if not runs["excre"][i].get("correct")
                    and runs[bn][i].get("correct"))
            p = mcnemar_exact(b, c)
            pvals.append(p)
            rows.append((bn, len(common), b, c, p))
        adj = holm(pvals) if pvals else []
        print("\n== excre vs baselines (exact McNemar, Holm-adjusted) ==")
        print(f"{'baseline':<16} {'n':>5} {'only-excre':>11} "
              f"{'only-base':>10} {'p':>8} {'p_adj':>8}")
        for (bn, n, b, c, p), pa in zip(rows, adj):
            print(f"{bn:<16} {n:>5} {b:>11} {c:>10} {p:>8.4f} {pa:>8.4f}")

    print("\n== gating signal vs correctness ==")
    print(f"{'system':<16} {'spearman':>9} {'AURC':>7} "
          f"{'acc@70%':>8} {'acc@80%':>8} {'acc@90%':>8}")
    for name, recs in runs.items():
        rs = [r for r in recs.values() if "signal" in r]
        if len(rs) < 10:
            continue
        sig = [r["signal"] for r in rs]
        cor = [1 if r.get("correct") else 0 for r in rs]
        rho = spearman(sig, cor)
        curve, aurc = risk_coverage(sig, cor)
        a70 = accuracy_at_coverage(curve, 0.7)
        a80 = accuracy_at_coverage(curve, 0.8)
        a90 = accuracy_at_coverage(curve, 0.9)
        print(f"{name:<16} {rho:>9.3f} {aurc:>7.3f} "
              f"{fmt_pct(a70):>8} {fmt_pct(a80):>8} {fmt_pct(a90):>8}")

    if "excre" in runs and "excre_adv" in runs:
        clean, adv = runs["excre"], runs["excre_adv"]
        common = sorted(set(clean) & set(adv))
        print(f"\n== adversarial insider ({len(common)} paired items) ==")
        for label, recs in (("clean", clean), ("sabotaged", adv)):
            rs = [recs[i] for i in common]
            acc = sum(1 for r in rs if r.get("correct")) / len(rs)
            tr = sum(r.get("trust", 0) for r in rs) / len(rs)
            fr = sum(r.get("fragility", 0) for r in rs) / len(rs)
            im = sum(r.get("imrc_coalition", {}).get("imrc", 0)
                     for r in rs) / len(rs)
            print(f"  {label:<10} acc {fmt_pct(acc)}  trust {tr:.3f}  "
                  f"coalition-IMRC {im:.3f}  fragility {fr:.3f}")
        # Adversarial detection via fragility metric
        pos = [adv[i].get("fragility", 0) for i in common]
        neg = [clean[i].get("fragility", 0) for i in common]
        print(f"  fragility AUROC (sabotaged vs clean): "
              f"{auroc(pos, neg):.3f}")
        flips = sum(1 for i in common
                    if clean[i].get("correct") and not adv[i].get("correct"))
        print(f"  consensus flipped to wrong on {flips}/{len(common)} items")

    # Convergence and schema compliance (excre runs carry the full trail)
    for name in ("excre", "excre_adv"):
        if name in runs:
            rs = list(runs[name].values())
            conv = sum(1 for r in rs if r.get("converged"))
            mean_rounds = sum(r.get("rounds_run", 0) for r in rs) / len(rs)
            print(f"\n{name}: converged early on {conv}/{len(rs)} items, "
                  f"mean rounds {mean_rounds:.2f}")
            per_model = defaultdict(lambda: [0, 0, 0])  # total, parsed, repaired
            for r in rs:
                for t in r.get("trail", []):
                    row = per_model[t["model"]]
                    row[0] += 1
                    row[1] += 1 if t["path"].get("parsed") else 0
                    row[2] += 1 if t.get("repaired") else 0
            if per_model:
                print(f"  schema compliance (valid after <=1 repair / "
                      f"repair used):")
                for mn, (tot, ok, rep) in sorted(per_model.items()):
                    print(f"    {mn:<16} {100 * ok / tot:5.1f}% valid, "
                          f"{100 * rep / tot:4.1f}% repaired  ({tot} calls)")


if __name__ == "__main__":
    main()

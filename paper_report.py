"""Paper tables from a run folder.

    python paper_report.py --run runs/v3
    python paper_report.py --run runs/v3 --nli      # adds the CARA baseline

Every signal is recomputed from the stored trails, so embedder or weight
variants cost no API calls. Writes analysis/report.md and analysis/items.csv
inside the run folder.
"""

import argparse
import csv
import glob
import os
import random
from collections import defaultdict

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from excre.config import load_config
from excre.data import is_correct, make_normaliser, read_jsonl
from excre.embed import build_sim
from excre.signals import debate_rounds, excre_signals, pair_scores, plurality
from excre.stats import (accuracy_at_coverage, holm, mcnemar_exact,
                         risk_coverage, wilson_ci)

SIGNALS = ["agreement", "confidence", "imrc_all", "imrc_coal", "imrc_coal_r0",
           "induced", "trust"]


def load_run(run):
    data, results = {}, {}
    for f in sorted(glob.glob(os.path.join(run, "data", "*.jsonl"))):
        ds = os.path.splitext(os.path.basename(f))[0]
        data[ds] = {it["id"]: it for it in read_jsonl(f)}
        results[ds] = {}
        for rf in sorted(glob.glob(os.path.join(run, ds, "*.jsonl"))):
            recs = {r["id"]: r for r in read_jsonl(rf) if "error" not in r}
            if recs:
                results[ds][os.path.splitext(os.path.basename(rf))[0]] = recs
    return data, results


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|---" * len(head) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return out + [""]


def pct(x):
    return f"{100 * x:.1f}"


def auc(scores, labels):
    if len(set(labels)) < 2:
        return None
    return roc_auc_score(labels, scores)


def auc_ci(scores, labels, iters, seed=0):
    """AUROC with a percentile bootstrap interval, as a table cell."""
    point = auc(scores, labels)
    if point is None:
        return "n/a"
    rng = random.Random(seed)
    n = len(labels)
    draws = []
    for _ in range(iters):
        idx = [rng.randrange(n) for _ in range(n)]
        a = auc([scores[i] for i in idx], [labels[i] for i in idx])
        if a is not None:
            draws.append(a)
    draws.sort()
    lo, hi = draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws)) - 1]
    return f"{point:.3f} [{lo:.3f}, {hi:.3f}]"


def flatten(data, results, simfn, cfg, extra):
    """plain[system] and rich[system]: one row per (dataset, item)."""
    plain, rich, pairs = defaultdict(list), defaultdict(list), []
    for ds, systems in results.items():
        items = data[ds]
        for name, recs in systems.items():
            for rid, r in recs.items():
                if rid not in items:
                    continue
                row = {"id": rid, "dataset": ds, "correct": bool(r.get("correct")),
                       "signal": r.get("signal", 0.5),
                       "tokens": r["tokens"]["prompt"] + r["tokens"]["completion"]}
                row["cut"] = r["tokens"].get("cut", 0)
                if name.startswith("mad"):
                    row["per_round"] = debate_rounds(r, items[rid])
                    sab = r.get("saboteur")
                    if sab:
                        norm = make_normaliser(items[rid]["format"])
                        target = norm(sab["target"])
                        row["sab_won"] = norm(r["answer"]) == target
                        row["sab_complied"] = norm(r["per_model"][sab["model"]]) == target
                plain[name].append(row)
                if name.startswith("excre"):
                    rich[name].append(excre_signals(r, items[rid], simfn, cfg, extra))
                    if name == "excre":
                        pairs += pair_scores(r, items[rid], simfn, cfg, extra)

        cots = sorted(n for n in systems if n.startswith("cot_"))
        if len(cots) >= 3:
            for rid in set.intersection(*(set(systems[n]) for n in cots)) & set(items):
                norm = make_normaliser(items[rid]["format"])
                ans = plurality([systems[n][rid]["answer"] for n in cots], norm)
                plain["cot_vote"].append({
                    "id": rid, "dataset": ds, "correct": is_correct(items[rid], ans),
                    "signal": 0.5,
                    "tokens": sum(systems[n][rid]["tokens"]["prompt"]
                                  + systems[n][rid]["tokens"]["completion"] for n in cots)})
        scs = sorted(n for n in systems if n.startswith("sc_"))
        if len(scs) >= 2:
            for rid in set.intersection(*(set(systems[n]) for n in scs)) & set(items):
                norm = make_normaliser(items[rid]["format"])
                samples = [a for n in scs for a in systems[n][rid]["samples"]]
                ans = plurality(samples, norm)
                share = sum(norm(a) == ans for a in samples) / len(samples)
                plain["sc_pool"].append({
                    "id": rid, "dataset": ds, "correct": is_correct(items[rid], ans),
                    "signal": share,
                    "tokens": sum(systems[n][rid]["tokens"]["prompt"]
                                  + systems[n][rid]["tokens"]["completion"] for n in scs)})
    for r in rich.get("excre", []):
        plain["excre_r0"].append({"id": r["id"], "dataset": r["dataset"],
                                  "correct": r["correct_r0"],
                                  "signal": r["agreement_r0"], "tokens": 0})
    return plain, rich, pairs


def accuracy_section(plain, datasets):
    lines = ["## 1. Accuracy", "",
             "Cells are accuracy % (n). cot_vote, sc_pool and excre_r0 are "
             "derived from other runs' outputs and cost no extra calls.", ""]
    rows = []
    for name in sorted(plain):
        cells = [name]
        for ds in datasets:
            sub = [r for r in plain[name] if r["dataset"] == ds]
            cells.append(f"{pct(sum(r['correct'] for r in sub) / len(sub))} ({len(sub)})"
                         if sub else "-")
        k, n = sum(r["correct"] for r in plain[name]), len(plain[name])
        p, lo, hi = wilson_ci(k, n)
        tok = sum(r["tokens"] for r in plain[name]) / n
        cells += [f"{pct(p)} [{pct(lo)}, {pct(hi)}]", n, f"{tok:.0f}"]
        rows.append(cells)
    lines += table(["system"] + datasets + ["pooled [95% CI]", "n", "tokens/item"], rows)

    if "excre" in plain:
        mine = {(r["dataset"], r["id"]): r["correct"] for r in plain["excre"]}
        rows, pvals = [], []
        for name in sorted(plain):
            if name.startswith("excre") or name.endswith("_adv"):
                continue
            theirs = {(r["dataset"], r["id"]): r["correct"] for r in plain[name]}
            common = set(mine) & set(theirs)
            b = sum(mine[i] and not theirs[i] for i in common)
            c = sum(theirs[i] and not mine[i] for i in common)
            pvals.append(mcnemar_exact(b, c))
            rows.append([name, len(common), b, c])
        for row, p, pa in zip(rows, pvals, holm(pvals)):
            row += [f"{p:.4f}", f"{pa:.4f}"]
        lines += ["Paired comparison with excre (exact McNemar, Holm-adjusted):", ""]
        lines += table(["baseline", "paired n", "only excre right",
                        "only baseline right", "p", "p (Holm)"], rows)
    return lines


def signal_section(rows, datasets, names, iters):
    lines = ["## 2. Which signals predict a correct consensus (C1)", "",
             "AUROC for telling right from wrong final answers, bootstrap 95% CI.", ""]
    scopes = [("pooled", rows)] + [(ds, [r for r in rows if r["dataset"] == ds])
                                   for ds in datasets]
    scopes = [(label, sub) for label, sub in scopes if sub]
    body = []
    for s in names:
        body.append([s] + [auc_ci([r[s] for r in sub], [r["correct"] for r in sub], iters)
                           for _, sub in scopes])
    lines += table(["signal"] + [f"{label} (n={len(sub)})" for label, sub in scopes], body)

    full = [r for r in rows if r["agreement"] == 1.0]
    if len(full) >= 20:
        lines += [f"Same test on the {len(full)} items where all agents gave the "
                  f"same answer, so answer agreement carries no information:", ""]
        lines += table(["signal", "AUROC"],
                       [[s, auc_ci([r[s] for r in full], [r["correct"] for r in full], iters)]
                        for s in names if s not in ("agreement", "trust")])

    lines += gain_table(rows, ["imrc_coal"], "IMRC", iters)
    return lines


def gain_table(rows, extra, label, iters):
    """Out-of-fold AUROC of agreement + confidence, with and without `extra`."""
    y = np.array([r["correct"] for r in rows], dtype=int)
    if min(y.sum(), len(y) - y.sum()) < 10:
        return []

    def oof(cols):
        X = np.array([[r[c] for c in cols] for r in rows])
        model = make_pipeline(StandardScaler(), LogisticRegression())
        folds = StratifiedKFold(5, shuffle=True, random_state=0)
        return cross_val_predict(model, X, y, cv=folds, method="predict_proba")[:, 1]
    base, plus = oof(["agreement", "confidence"]), oof(["agreement", "confidence"] + extra)
    rng = random.Random(0)
    diffs = []
    for _ in range(iters):
        idx = [rng.randrange(len(y)) for _ in y]
        if len(set(y[idx])) == 2:
            diffs.append(roc_auc_score(y[idx], plus[idx]) - roc_auc_score(y[idx], base[idx]))
    diffs.sort()
    lines = ["Logistic regression on correctness, 5-fold out-of-fold AUROC:", ""]
    return lines + table(["features", "AUROC"], [
        ["agreement + confidence", f"{roc_auc_score(y, base):.3f}"],
        [f"agreement + confidence + {label}", f"{roc_auc_score(y, plus):.3f}"],
        [f"gain from {label} [95% CI]",
         f"{roc_auc_score(y, plus) - roc_auc_score(y, base):+.3f} "
         f"[{diffs[int(0.025 * len(diffs))]:+.3f}, {diffs[int(0.975 * len(diffs)) - 1]:+.3f}]"]])


# fixed in PREREGISTRATION.md on 22 Nov 2026, before any of these items ran
CONFIRM_FROM = 32


def confirmation_section(rich, iters):
    scopes = [(f"excre, questions {CONFIRM_FROM + 1}+",
               [r for r in rich.get("excre", []) if question_index(r) >= CONFIRM_FROM]),
              ("excre_stepsfirst, all", rich.get("excre_stepsfirst", []))]
    scopes = [(label, rs) for label, rs in scopes if rs]
    if not scopes:
        return []
    lines = ["## 2b. Pre-registered confirmation (PREREGISTRATION.md)", "",
             "H1: coalition IMRC before the exchange > 0.5. H2: the rise in "
             "coalition IMRC during the exchange flags wrong answers (AUROC of "
             "-induced > 0.5). H3: final coalition IMRC is not above 0.5. "
             "H4: round-0 IMRC and induced add to agreement + confidence.", ""]
    body = []
    for label, rs in scopes:
        y = [r["correct"] for r in rs]
        body.append([label, len(rs), len(rs) - sum(y),
                     auc_ci([r["imrc_coal_r0"] for r in rs], y, iters),
                     auc_ci([-r["induced"] for r in rs], y, iters),
                     auc_ci([r["imrc_coal"] for r in rs], y, iters),
                     auc_ci([r["confidence"] for r in rs], y, iters)])
    lines += table(["items", "n", "wrong", "H1 IMRC r0", "H2 -induced",
                    "H3 final IMRC", "confidence (reference)"], body)
    for label, rs in scopes:
        part = gain_table(rs, ["imrc_coal_r0", "induced"], "IMRC r0 + induced", iters)
        if part:
            lines += [f"H4 on {label}:", ""] + part
    return lines


def question_index(row):
    return int(row["id"].rsplit("-", 1)[1])


def selective_section(plain, rows):
    lines = ["## 3. Selective prediction (C2)", "",
             "Answer only the most trusted share of items. AURC: lower is better.", ""]
    gates = [(f"excre / {s}", [r[s] for r in rows], [r["correct"] for r in rows])
             for s in ("trust", "agreement", "confidence", "imrc_coal")]
    for name in sorted(plain):
        if name.startswith(("sc_", "mad", "reconcile")):
            gates.append((f"{name} / own signal", [r["signal"] for r in plain[name]],
                          [r["correct"] for r in plain[name]]))
    body = []
    for label, sig, cor in gates:
        if len(cor) < 10:
            continue
        curve, aurc = risk_coverage(sig, cor)
        body.append([label, len(cor), f"{aurc:.3f}", pct(sum(cor) / len(cor))]
                    + [pct(accuracy_at_coverage(curve, c)) for c in (0.9, 0.8, 0.7)])
    return lines + table(["gate", "n", "AURC", "acc@100%", "acc@90%", "acc@80%", "acc@70%"], body)


def saboteur_section(plain, rich, names, iters):
    clean = {(r["dataset"], r["id"]): r for r in rich.get("excre", [])}
    adv = {(r["dataset"], r["id"]): r for r in rich.get("excre_adv", [])}
    common = sorted(set(clean) & set(adv))
    if not common:
        return []
    lines = ["## 4. Adversarial insider (C3)", "",
             f"{len(common)} items run twice: clean, and with one agent secretly "
             f"arguing for a fixed wrong answer.", ""]
    rows = []
    for label, a, b in (("excre", clean, adv),
                        ("mad", {(r["dataset"], r["id"]): r for r in plain.get("mad", [])},
                         {(r["dataset"], r["id"]): r for r in plain.get("mad_adv", [])})):
        both = sorted(set(a) & set(b))
        if both:
            rows.append([label, len(both),
                         pct(sum(a[i]["correct"] for i in both) / len(both)),
                         pct(sum(b[i]["correct"] for i in both) / len(both)),
                         sum(a[i]["correct"] and not b[i]["correct"] for i in both),
                         pct(sum(b[i]["sab_complied"] for i in both) / len(both)),
                         pct(sum(b[i]["sab_won"] for i in both) / len(both))])
    lines += table(["system", "paired n", "clean acc", "sabotaged acc",
                    "right -> wrong", "saboteur ended on its target %",
                    "consensus = target %"], rows)

    flip = {"fragility": 1, "induced": 1}
    body = []
    for s in ["fragility"] + [n for n in names if n != "induced"] + ["induced"]:
        sign = flip.get(s, -1)
        scores = [sign * adv[i][s] for i in common] + [sign * clean[i][s] for i in common]
        labels = [1] * len(common) + [0] * len(common)
        body.append([s if sign > 0 else f"low {s}", auc_ci(scores, labels, iters)])
    lines += ["Telling sabotaged runs from clean ones (AUROC, 0.5 = chance):", ""]
    lines += table(["flag", "AUROC [95% CI]"], body)

    hit = [adv[i] for i in common]
    by_model = defaultdict(list)
    for r in hit:
        by_model[r["saboteur"]].append(r)
    body = [[m, len(rs), pct(sum(r["sab_won"] for r in rs) / len(rs)),
             pct(sum(r["outlier"] == m for r in rs) / len(rs)),
             pct(sum(r["minority"] == m for r in rs) / len(rs))]
            for m, rs in sorted(by_model.items())]
    body.append(["all", len(hit), pct(sum(r["sab_won"] for r in hit) / len(hit)),
                 pct(sum(r["outlier"] == r["saboteur"] for r in hit) / len(hit)),
                 pct(sum(r["minority"] == r["saboteur"] for r in hit) / len(hit))])
    lines += ["Naming the saboteur. Outlier = the agent whose final path is least "
              "congruent with the others; chance is one in the number of agents.", ""]
    lines += table(["saboteur", "n", "consensus = its target %",
                    "caught as IMRC outlier %", "caught as lone dissenter %"], body)
    return lines


def ablation_section(plain, rich):
    variants = [n for n in rich if n not in ("excre", "excre_adv")]
    if not variants or "excre" not in rich:
        return []
    lines = ["## 5. Ablations and matched free-text debate (C4)", "",
             "Each variant against the full system on the items both have.", ""]
    full = {(r["dataset"], r["id"]): r for r in rich["excre"]}
    mad = {(r["dataset"], r["id"]): r for r in plain.get("mad", [])}
    body = []
    for name in sorted(variants):
        theirs = {(r["dataset"], r["id"]): r for r in rich[name]}
        common = sorted(set(full) & set(theirs))
        if not common:
            continue
        for label, src in ((f"excre (items of {name})", full), (name, theirs)):
            rs = [src[i] for i in common]
            y = [r["correct"] for r in rs]
            cells = [auc([r[s] for r in rs], y) for s in ("imrc_coal", "imrc_coal_r0")]
            cells.append(auc([-r["induced"] for r in rs], y))
            body.append([label, len(rs), pct(sum(r["correct_r0"] for r in rs) / len(rs)),
                         pct(sum(y) / len(rs)),
                         f"{np.mean([r['rounds'] for r in rs]):.2f}",
                         f"{np.mean([r['tokens'] for r in rs]):.0f}",
                         f"{np.mean([r['imrc_coal'] for r in rs]):.3f}"]
                        + [f"{a:.3f}" if a is not None else "n/a" for a in cells])
        both = [i for i in common if i in mad]
        if both and name.endswith("bare"):
            body.append(["mad", len(both), "-", pct(sum(mad[i]["correct"] for i in both) / len(both)),
                         "-", f"{np.mean([mad[i]['tokens'] for i in both]):.0f}", "-", "-", "-", "-"])
    return lines + table(["system", "n", "r0 acc", "acc", "rounds", "tokens/item",
                          "mean IMRC", "IMRC AUROC", "IMRC r0 AUROC",
                          "-induced AUROC"], body)


def dynamics_section(plain, rows):
    lines = ["## 6. What the exchange rounds do", ""]
    depth = max(len(r["per_round"]) for r in rows)
    body = []
    for k in range(depth):
        at = [r["per_round"][min(k, len(r["per_round"]) - 1)] for r in rows]
        cells = [k, pct(np.mean([a["correct"] for a in at])),
                 f"{np.mean([a['agreement'] for a in at]):.3f}",
                 f"{np.mean([a['imrc'] for a in at]):.3f}"]
        mad = [r["per_round"][min(k, len(r["per_round"]) - 1)]
               for r in plain.get("mad", []) if r.get("per_round")]
        cells += ([pct(np.mean([a["correct"] for a in mad])),
                   f"{np.mean([a['agreement'] for a in mad]):.3f}"] if mad else ["-", "-"])
        body.append(cells)
    lines += table(["round", "excre acc", "excre agreement", "excre IMRC",
                    "mad acc", "mad agreement"], body)
    fixed = sum(r["correct"] and not r["correct_r0"] for r in rows)
    broke = sum(r["correct_r0"] and not r["correct"] for r in rows)
    lines += [f"excre, round 0 to final: {fixed} wrong -> right, {broke} right -> wrong "
              f"(of {len(rows)}).", ""]
    mad = [r for r in plain.get("mad", []) if r.get("per_round")]
    if mad:
        fixed = sum(r["per_round"][-1]["correct"] and not r["per_round"][0]["correct"] for r in mad)
        broke = sum(r["per_round"][0]["correct"] and not r["per_round"][-1]["correct"] for r in mad)
        lines += [f"mad, round 0 to final: {fixed} wrong -> right, {broke} right -> wrong "
                  f"(of {len(mad)}).", ""]
    return lines


def checks_section(results, plain, rows, pairs, extra, iters):
    lines = ["## 7. Metric and protocol checks", ""]
    if len({p["same"] for p in pairs}) == 2:
        lines += ["Agent pairs with the same answer vs different answers (AUROC):", ""]
        lines += table(["metric", "AUROC [95% CI]"],
                       [[m, auc_ci([p[m] for p in pairs], [p["same"] for p in pairs], iters)]
                        for m in ["imrc"] + list(extra)])
    lone = sum(not r["defined"] for r in rows)
    lines += [f"No two agents shared the final answer on {lone}/{len(rows)} items "
              f"(coalition IMRC undefined, scored 0). Early convergence on "
              f"{sum(r['converged'] for r in rows)}/{len(rows)}, mean rounds "
              f"{np.mean([r['rounds'] for r in rows]):.2f}.", ""]
    calls = defaultdict(lambda: [0, 0, 0, 0, 0])
    for systems in results.values():
        for name in ("excre", "excre_stepsfirst"):
            for r in systems.get(name, {}).values():
                for t in r["trail"]:
                    c = calls[name, t["model"]]
                    c[0] += 1
                    c[1] += bool(t["path"].get("parsed"))
                    c[2] += bool(t.get("repaired"))
                    c[3] += bool(t.get("truncated"))
                    # did the reply really put its steps ahead of its answer
                    s, a = t["raw"].find('"steps"'), t["raw"].find('"answer"')
                    c[4] += 0 <= s < a
    lines += table(["system", "model", "replies", "valid schema %", "needed repair %",
                    "hit token cap %", "steps before answer %"],
                   [[name, m, c[0], pct(c[1] / c[0]), pct(c[2] / c[0]), pct(c[3] / c[0]),
                     pct(c[4] / c[0])]
                    for (name, m), c in sorted(calls.items())])
    cut = {name: sum(r.get("cut", 0) for r in rs) for name, rs in plain.items()}
    if any(cut.values()):
        lines += ["Baseline replies that hit the token cap: "
                  + ", ".join(f"{n} {c}" for n, c in sorted(cut.items()) if c) + ".", ""]
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=os.path.join("runs", "v3"))
    ap.add_argument("--config", default=os.path.join("configs", "main.yaml"))
    ap.add_argument("--embedder", default=None, help="override imrc.embedder")
    ap.add_argument("--nli", action="store_true",
                    help="add the CARA-HYB baseline (downloads an NLI model)")
    ap.add_argument("--boot", type=int, default=1000)
    args = ap.parse_args()

    cfg = load_config(args.config)
    if args.embedder:
        cfg["imrc"]["embedder"] = args.embedder
    simfn = build_sim(cfg["imrc"])
    extra = {}
    if args.nli:
        from excre.cara import Contradiction, cara_group
        nli = Contradiction()
        extra["cara"] = lambda paths: cara_group(paths, simfn, nli)

    data, results = load_run(args.run)
    datasets = [ds for ds in data if results[ds]]
    plain, rich, pairs = flatten(data, results, simfn, cfg, extra)
    rows = rich.get("excre", [])
    if not rows:
        raise SystemExit(f"no excre results under {args.run} yet")
    names = SIGNALS + list(extra)

    lines = [f"# {args.run}", "",
             f"embedder {simfn.name}, IMRC weights "
             f"{cfg['imrc']['alpha']}/{cfg['imrc']['beta']}/{cfg['imrc']['gamma']}, "
             f"{len(rows)} excre items over {', '.join(datasets)}", ""]
    lines += accuracy_section(plain, datasets)
    lines += signal_section(rows, datasets, names, args.boot)
    lines += confirmation_section(rich, args.boot)
    lines += selective_section(plain, rows)
    lines += saboteur_section(plain, rich, names, args.boot)
    lines += ablation_section(plain, rich)
    lines += dynamics_section(plain, rows)
    lines += checks_section(results, plain, rows, pairs, extra, args.boot)

    out = os.path.join(args.run, "analysis")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    cols = [c for c in rows[0] if c != "per_round"]
    with open(os.path.join(out, "items.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["system"] + cols, extrasaction="ignore")
        w.writeheader()
        for name, rs in sorted(rich.items()):
            for r in rs:
                w.writerow(dict(r, system=name))
    print(f"wrote {out}/report.md and items.csv "
          f"({sum(len(v) for v in rich.values())} excre-type rows)")


if __name__ == "__main__":
    main()

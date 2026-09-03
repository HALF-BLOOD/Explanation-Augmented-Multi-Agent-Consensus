"""Statistical evaluation utilities: confidence intervals, hypothesis testing, correlation, and selective prediction metrics."""

import math
import random


def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (p, max(0.0, centre - half), min(1.0, centre + half))


def mcnemar_exact(b, c):
    """Two-sided exact McNemar test on discordant pair counts."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def _ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def spearman(xs, ys):
    return pearson(_ranks(xs), _ranks(ys))


def auroc(scores_pos, scores_neg):
    """Mann-Whitney formulation; ties count half."""
    if not scores_pos or not scores_neg:
        return 0.5
    wins = ties = 0
    for p in scores_pos:
        for q in scores_neg:
            if p > q:
                wins += 1
            elif p == q:
                ties += 1
    return (wins + 0.5 * ties) / (len(scores_pos) * len(scores_neg))


def risk_coverage(signals, corrects):
    """Sort by signal descending, sweep coverage. Returns the curve as
    (coverage, accuracy) points plus AURC (area under risk-coverage,
    lower = better)."""
    order = sorted(range(len(signals)), key=lambda i: -signals[i])
    curve = []
    right = 0
    risk_sum = 0.0
    for rank, i in enumerate(order, start=1):
        right += 1 if corrects[i] else 0
        risk = 1 - right / rank
        risk_sum += risk
        curve.append((rank / len(order), right / rank))
    aurc = risk_sum / len(order)
    return curve, aurc


def accuracy_at_coverage(curve, coverage):
    """Accuracy at the largest coverage <= requested (curve is sorted)."""
    best = None
    for cov, acc in curve:
        if cov <= coverage + 1e-9:
            best = acc
    return best if best is not None else (curve[0][1] if curve else 0.0)


def bootstrap_ci(values_fn, n_items, iters=2000, seed=0, alpha=0.05):
    """Generic percentile bootstrap: values_fn(indices) -> statistic."""
    rng = random.Random(seed)
    stats = []
    idx = list(range(n_items))
    for _ in range(iters):
        sample = [rng.choice(idx) for _ in idx]
        stats.append(values_fn(sample))
    stats.sort()
    lo = stats[int(alpha / 2 * iters)]
    hi = stats[int((1 - alpha / 2) * iters) - 1]
    return lo, hi


def holm(pvalues):
    """Holm-Bonferroni adjusted p-values, order preserved."""
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    adjusted = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * pvalues[i])
        adjusted[i] = min(1.0, running)
    return adjusted

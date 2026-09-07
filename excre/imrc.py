"""Inter-Model Reasoning Congruence (IMRC).

Computes pairwise semantic, structural, and evidence congruence:
    IMRC(R_i, R_j) = alpha * S_semantic + beta * S_structural + gamma * S_evidence
"""

from itertools import combinations

try:
    from scipy.optimize import linear_sum_assignment
    _HAVE_SCIPY = True
except ImportError:
    _HAVE_SCIPY = False


def _assign(sim_matrix, n_a, n_b):
    """Return list of (i, j, sim) matches, one-to-one."""
    if not n_a or not n_b:
        return []
    if _HAVE_SCIPY:
        cost = [[-sim_matrix[(i, j)] for j in range(n_b)] for i in range(n_a)]
        rows, cols = linear_sum_assignment(cost)
        return [(i, j, sim_matrix[(i, j)]) for i, j in zip(rows, cols)]
    matches, used_a, used_b = [], set(), set()
    for (i, j), s in sorted(sim_matrix.items(), key=lambda kv: -kv[1]):
        if i in used_a or j in used_b:
            continue
        matches.append((i, j, s))
        used_a.add(i)
        used_b.add(j)
    return matches


def semantic(a, b, simfn):
    sa, sb = a["steps"], b["steps"]
    if not sa or not sb:
        return 0.0, []
    sims = {(i, j): simfn.sim(x["claim"], y["claim"])
            for i, x in enumerate(sa) for j, y in enumerate(sb)}
    matches = _assign(sims, len(sa), len(sb))
    score = sum(s for _, _, s in matches) / max(len(sa), len(sb))
    return score, matches


def structural(a, b, matches):
    la, lb = len(a["steps"]), len(b["steps"])
    if not la or not lb:
        return 0.0
    parts = [min(la, lb) / max(la, lb)]

    # Check step order concordance
    pairs = sorted((i, j) for i, j, s in matches if s > 0)
    if len(pairs) >= 2:
        concordant = total = 0
        for x in range(len(pairs)):
            for y in range(x + 1, len(pairs)):
                total += 1
                if (pairs[x][1] < pairs[y][1]) == (pairs[x][0] < pairs[y][0]):
                    concordant += 1
        parts.append(concordant / total)

    ea, eb = _dep_edges(a), _dep_edges(b)
    if ea or eb:
        union = ea | eb
        parts.append(len(ea & eb) / len(union))

    return sum(parts) / len(parts)


def _dep_edges(path):
    # Map step IDs to sequence positions
    pos = {s["id"]: k for k, s in enumerate(path["steps"])}
    edges = set()
    for k, s in enumerate(path["steps"]):
        for d in s.get("depends_on", []):
            if d in pos and pos[d] != k:
                edges.add((pos[d], k))
    return edges


def evidence(a, b, simfn, threshold=0.5):
    sa = [s for s in a["steps"] if s["evidence"]]
    sb = [s for s in b["steps"] if s["evidence"]]
    if not sa or not sb:
        return 0.0
    sims = {(i, j): simfn.sim(x["evidence"], y["evidence"])
            for i, x in enumerate(sa) for j, y in enumerate(sb)}
    score = 0.0
    for i, j, s in _assign(sims, len(sa), len(sb)):
        if s >= threshold:
            score += min(sa[i]["weight"], sb[j]["weight"])
    return score


def imrc_pair(a, b, simfn, weights, evidence_threshold=0.5):
    sem, matches = semantic(a, b, simfn)
    struc = structural(a, b, matches)
    ev = evidence(a, b, simfn, evidence_threshold)
    alpha, beta, gamma = weights
    return {
        "semantic": sem,
        "structural": struc,
        "evidence": ev,
        "imrc": alpha * sem + beta * struc + gamma * ev,
    }


def imrc_group(paths, simfn, weights, evidence_threshold=0.5):
    """Mean pairwise IMRC over a set of reasoning paths (with breakdown)."""
    if len(paths) < 2:
        return {"semantic": 1.0, "structural": 1.0, "evidence": 1.0,
                "imrc": 1.0, "pairs": 0}
    acc = {"semantic": 0.0, "structural": 0.0, "evidence": 0.0, "imrc": 0.0}
    n = 0
    for a, b in combinations(paths, 2):
        p = imrc_pair(a, b, simfn, weights, evidence_threshold)
        for k in acc:
            acc[k] += p[k]
        n += 1
    out = {k: v / n for k, v in acc.items()}
    out["pairs"] = n
    return out

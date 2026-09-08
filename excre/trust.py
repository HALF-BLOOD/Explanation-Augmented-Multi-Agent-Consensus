"""Consensus aggregation, trust scoring, and reasoning fragility computation."""

from collections import Counter


def consensus_answer(paths, normalise):
    """Majority over normalised answers; confidence-weighted tie-break."""
    votes = Counter()
    weight = Counter()
    for p in paths:
        key = normalise(p["answer"])
        votes[key] += 1
        weight[key] += p["confidence"]
    best = max(votes, key=lambda k: (votes[k], weight[k]))
    return best, votes[best] / len(paths)


def coalition(paths, answer, normalise):
    return [p for p in paths if normalise(p["answer"]) == answer]


def trust_components(coalition_paths, imrc_all, imrc_coalition, agreement,
                     converged):
    conf = ([p["confidence"] for p in coalition_paths] or [0.0])
    return {
        "agreement": agreement,
        "imrc_all": imrc_all,
        "imrc_coalition": imrc_coalition,
        "mean_confidence": sum(conf) / len(conf),
        "converged": 1.0 if converged else 0.0,
    }


def trust_score(components, weights):
    """Compute weighted trust score across agreement, IMRC, and confidence."""
    pairs = [
        (weights.get("w_agreement", 0.35), components["agreement"]),
        (weights.get("w_imrc", 0.35), components["imrc_coalition"]),
        (weights.get("w_confidence", 0.20), components["mean_confidence"]),
        (weights.get("w_converged", 0.10), components["converged"]),
    ]
    total = sum(w for w, _ in pairs)
    if total <= 0:
        return 0.0
    return sum(w * v for w, v in pairs) / total


def fragility(agreement, imrc_coalition):
    """Measure divergence between answer agreement and rationale congruence."""
    return agreement * (1.0 - imrc_coalition)

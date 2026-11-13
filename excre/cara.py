"""CARA-HYB (Wang & Yang 2026, "The Consistency Illusion") as a baseline metric.

Step pairs score -1 when an NLI model calls them a contradiction and their
embedding cosine otherwise; every step takes its best match on the other
side, the two directions are averaged, and the result is rescaled to [0, 1].
Steps are our schema's claims, where the paper splits free text by sentence.
"""

from itertools import combinations


class Contradiction:
    def __init__(self, name="cross-encoder/nli-deberta-v3-base"):
        from sentence_transformers import CrossEncoder
        self.model = CrossEncoder(name)
        labels = self.model.model.config.id2label
        self.index = next(i for i, lab in labels.items()
                          if lab.lower().startswith("contra"))
        self.memo = {}

    def probs(self, pairs):
        new = [p for p in set(pairs) if p not in self.memo]
        if new:
            scores = self.model.predict(new, apply_softmax=True,
                                        show_progress_bar=False)
            for p, s in zip(new, scores):
                self.memo[p] = float(s[self.index])
        return [self.memo[p] for p in pairs]


def _claims(path):
    return [s["claim"] for s in path["steps"] if s["claim"].strip()]


def cara_pair(a, b, simfn, nli, threshold=0.7):
    """Raw CARA in [-1, 1] plus the share of best matches that contradict."""
    ca, cb = _claims(a), _claims(b)
    if not ca or not cb:
        return 0.0, 0.0
    grid = [(x, y) for x in ca for y in cb]
    clash = [max(p, q) > threshold for p, q in
             zip(nli.probs(grid), nli.probs([(y, x) for x, y in grid]))]
    score = {pair: (-1.0 if bad else simfn.sim(*pair))
             for pair, bad in zip(grid, clash)}

    a_best = [max(score[x, y] for y in cb) for x in ca]
    b_best = [max(score[x, y] for x in ca) for y in cb]
    raw = 0.5 * (sum(a_best) / len(a_best) + sum(b_best) / len(b_best))
    best = a_best + b_best
    return raw, sum(1 for s in best if s < 0) / len(best)


def cara_group(paths, simfn, nli, threshold=0.7):
    """Mean pairwise CARA, rescaled to [0, 1] as in the paper's Eq. 7."""
    pairs = list(combinations(paths, 2))
    if not pairs:
        return 0.0
    raw = sum(cara_pair(a, b, simfn, nli, threshold)[0] for a, b in pairs)
    return (raw / len(pairs) + 1) / 2

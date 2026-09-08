import math

from excre.data import (is_correct, normalise_letter, normalise_numeric,
                        normalise_yesno)
from excre.stats import (auroc, holm, mcnemar_exact, risk_coverage, spearman,
                         wilson_ci)
from excre.trust import consensus_answer, fragility, trust_score


def test_normalisers():
    assert normalise_numeric("$1,234.00") == "1234"
    assert normalise_numeric("The answer is 42.") == "42"
    assert normalise_numeric("3/4") == "0.75"
    assert normalise_numeric("650 rupees") == "650"
    assert normalise_letter("(B) because...") == "B"
    assert normalise_letter("b") == "B"
    assert normalise_letter("C.") == "C"
    assert normalise_yesno("Yes, definitely") == "yes"
    assert normalise_yesno("FALSE") == "no"


def test_is_correct_uses_format():
    item = {"format": "numeric", "gold": "117"}
    assert is_correct(item, " 117 rolls")
    assert not is_correct(item, "116")


def test_consensus_majority_and_tiebreak():
    def norm(x):
        return x.strip().lower()
    paths = [{"answer": "A", "confidence": 0.9},
             {"answer": "a", "confidence": 0.6},
             {"answer": "B", "confidence": 0.99}]
    ans, agreement = consensus_answer(paths, norm)
    assert ans == "a"
    assert abs(agreement - 2 / 3) < 1e-9
    # tie: confidence decides
    paths = [{"answer": "A", "confidence": 0.5},
             {"answer": "B", "confidence": 0.95}]
    ans, _ = consensus_answer(paths, norm)
    assert ans == "b"


def test_trust_monotone_in_imrc():
    w = {"w_agreement": 0.35, "w_imrc": 0.35, "w_confidence": 0.2,
         "w_converged": 0.1}
    base = {"agreement": 0.66, "imrc_coalition": 0.3, "mean_confidence": 0.7,
            "converged": 1.0}
    hi = dict(base, imrc_coalition=0.9)
    assert trust_score(hi, w) > trust_score(base, w)


def test_fragility_peaks_on_agree_what_disagree_why():
    assert fragility(1.0, 0.1) > fragility(1.0, 0.9)
    assert fragility(1.0, 0.1) > fragility(0.4, 0.1)


def test_wilson():
    p, lo, hi = wilson_ci(80, 100)
    assert abs(p - 0.8) < 1e-9
    assert lo < 0.8 < hi
    assert 0.70 < lo < 0.73  # textbook value ~0.711


def test_mcnemar():
    assert mcnemar_exact(0, 0) == 1.0
    assert mcnemar_exact(5, 5) == 1.0
    assert mcnemar_exact(15, 2) < 0.01


def test_spearman_extremes():
    xs = [1, 2, 3, 4, 5]
    assert abs(spearman(xs, [2, 4, 6, 8, 10]) - 1.0) < 1e-9
    assert abs(spearman(xs, [10, 8, 6, 4, 2]) + 1.0) < 1e-9


def test_auroc_known():
    assert auroc([0.9, 0.8], [0.1, 0.2]) == 1.0
    assert auroc([0.1], [0.9]) == 0.0
    # pairs: one tie (0.5 vs 0.5) and three wins -> (3 + 0.5) / 4
    assert abs(auroc([0.5, 0.7], [0.5, 0.3]) - 0.875) < 1e-9


def test_risk_coverage_perfect_ranking():
    # signal perfectly separates correct from wrong
    signals = [0.9, 0.8, 0.7, 0.2, 0.1]
    correct = [1, 1, 1, 0, 0]
    curve, aurc = risk_coverage(signals, correct)
    assert curve[0][1] == 1.0          # top item is right
    assert abs(curve[-1][0] - 1.0) < 1e-9
    _, aurc_bad = risk_coverage(signals, [0, 0, 1, 1, 1])
    assert aurc < aurc_bad


def test_holm_orders():
    adj = holm([0.01, 0.04, 0.03])
    assert adj[0] == 0.03
    assert all(0 <= p <= 1 for p in adj)
    assert not math.isnan(sum(adj))

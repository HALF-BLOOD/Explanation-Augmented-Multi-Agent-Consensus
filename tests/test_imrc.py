from excre.embed import LexicalSim
from excre.imrc import imrc_group, imrc_pair

W = (0.5, 0.2, 0.3)
SIM = LexicalSim()


def path(steps, answer="42"):
    n = len(steps)
    return {"answer": answer, "confidence": 0.8, "parsed": True,
            "considered": [],
            "steps": [{"id": i + 1, "claim": c, "evidence": e,
                       "weight": 1.0 / n, "depends_on": d}
                      for i, (c, e, d) in enumerate(steps)]}


A = path([
    ("add the morning and afternoon trays together", "seven plus four trays", []),
    ("multiply trays by rolls per tray", "eleven times twelve rolls", [1]),
    ("subtract the rolls kept for family", "fifteen rolls kept", [2]),
])


def test_identical_paths_score_high():
    r = imrc_pair(A, A, SIM, W)
    assert r["semantic"] > 0.99
    assert r["structural"] > 0.99
    assert r["evidence"] > 0.99
    assert r["imrc"] > 0.99


def test_disjoint_paths_score_low():
    b = path([
        ("check the capital city of the country", "geography atlas entry", []),
        ("compare population figures", "census data table", [1]),
    ])
    r = imrc_pair(A, b, SIM, W)
    assert r["semantic"] < 0.2
    assert r["evidence"] < 0.1
    assert r["imrc"] < 0.4


def test_symmetry():
    b = path([
        ("multiply trays by rolls per tray", "eleven times twelve rolls", []),
        ("subtract the family rolls", "fifteen kept back", [1]),
    ])
    assert abs(imrc_pair(A, b, SIM, W)["imrc"]
               - imrc_pair(b, A, SIM, W)["imrc"]) < 1e-9


def test_padding_does_not_inflate_semantic():
    padded = path([(s["claim"], s["evidence"], []) for s in A["steps"]]
                  + [("irrelevant extra step", "made up", []),
                     ("another filler", "also made up", [])])
    r_same = imrc_pair(A, A, SIM, W)
    r_padded = imrc_pair(A, padded, SIM, W)
    assert r_padded["semantic"] < r_same["semantic"]


def test_empty_steps_guard():
    empty = path([])
    r = imrc_pair(A, empty, SIM, W)
    assert r["imrc"] == 0.0


def test_group_mean_and_single():
    assert imrc_group([A], SIM, W)["imrc"] == 1.0
    g = imrc_group([A, A, A], SIM, W)
    assert g["pairs"] == 3
    assert g["imrc"] > 0.99


def test_order_disagreement_lowers_structural():
    reversed_b = path([(s["claim"], s["evidence"], [])
                       for s in reversed(A["steps"])])
    same_b = path([(s["claim"], s["evidence"], []) for s in A["steps"]])
    r_rev = imrc_pair(A, reversed_b, SIM, W)
    r_same = imrc_pair(A, same_b, SIM, W)
    assert r_rev["structural"] < r_same["structural"]

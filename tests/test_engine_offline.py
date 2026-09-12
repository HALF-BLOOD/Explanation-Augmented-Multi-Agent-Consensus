"""End-to-end offline tests verifying pipeline components on mock models."""

from excre.baselines import run_mad, run_reconcile, run_self_consistency
from excre.embed import LexicalSim
from excre.engine import run_excre
from excre.llm import MockModel
from excre.runner import plausible_wrong_answer

CFG = {
    "excre": {"rounds": 2, "devils_advocate": True, "anchor": True,
              "convergence_eps": 0.02, "temperature": 0.3, "max_tokens": 900},
    "imrc": {"alpha": 0.5, "beta": 0.2, "gamma": 0.3,
             "evidence_threshold": 0.5},
    "trust": {"w_agreement": 0.35, "w_imrc": 0.35, "w_confidence": 0.2,
              "w_converged": 0.1},
    "sc": {"k": 3, "temperature": 0.7},
    "judge": {"model": None},
}

ITEM = {"id": "t-1", "dataset": "dev", "format": "numeric",
        "question": "A tank is filled at 35 litres per minute for 8 minutes,"
                    " and then 60 litres are drained. How many litres remain?",
        "choices": None, "gold": "220", "meta": {}}

MODELS = [MockModel("m1", persona=1), MockModel("m2", persona=2),
          MockModel("m3", persona=5)]
SIM = LexicalSim()


def test_excre_record_shape():
    rec = run_excre(ITEM, MODELS, SIM, CFG)
    assert rec["system"] == "excre"
    assert rec["answer"]
    assert 0.0 <= rec["trust"] <= 1.0
    assert set(rec["components"]) >= {"agreement", "imrc_coalition",
                                      "mean_confidence", "converged"}
    assert rec["rounds_run"] >= 1
    assert rec["tokens"]["completion"] > 0
    rounds_seen = {t["round"] for t in rec["trail"]}
    assert 0 in rounds_seen
    assert len(rec["trail"]) == len(MODELS) * (rec["rounds_run"] + 1)


def test_excre_deterministic_with_mocks():
    a = run_excre(ITEM, MODELS, SIM, CFG)
    b = run_excre(ITEM, MODELS, SIM, CFG)
    assert a["answer"] == b["answer"]
    assert a["trust"] == b["trust"]


def test_saboteur_pushes_target():
    target = plausible_wrong_answer(ITEM)
    rec = run_excre(ITEM, MODELS, SIM, CFG,
                    saboteur={"model": "m2", "target": target})
    assert rec["saboteur"]["model"] == "m2"
    assert rec["per_model"]["m2"]["answer"] == target
    assert rec["per_model"]["m2"]["confidence"] >= 0.85


def test_plausible_wrong_answer_is_wrong():
    from excre.data import make_normaliser
    for item in (ITEM,
                 {"format": "yesno", "gold": "yes", "choices": None},
                 {"format": "letter", "gold": "B",
                  "choices": ["w", "x", "y", "z"]}):
        norm = make_normaliser(item["format"])
        assert norm(plausible_wrong_answer(item)) != norm(item["gold"])


def test_baselines_run():
    sc = run_self_consistency(ITEM, MODELS[0], CFG)
    assert sc["system"] == "sc_m1"
    assert 0 < sc["signal"] <= 1.0
    mad = run_mad(ITEM, MODELS, CFG, rounds=1)
    assert mad["answer"]
    assert mad["tokens"]["completion"] > 0
    rc = run_reconcile(ITEM, MODELS, CFG, rounds=1)
    assert rc["answer"]
    assert 0 < rc["signal"] <= 1.0

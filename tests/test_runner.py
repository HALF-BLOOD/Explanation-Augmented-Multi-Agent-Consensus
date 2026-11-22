import time

import pytest

from excre.data import read_jsonl
from excre.llm import MockModel, ModelUnavailable
from excre.runner import models_needed, run_system
from test_engine_offline import CFG, MODELS, SIM

ITEMS = [{"id": f"t-{i}", "dataset": "dev", "format": "numeric",
          "question": f"Add {i} and {i + 3}.", "choices": None,
          "gold": str(2 * i + 3), "meta": {}} for i in range(6)]


class DeadModel(MockModel):
    def chat(self, *a, **kw):
        raise ModelUnavailable(self.name, "daily quota used up")


def test_saboteur_rotation_survives_resume(tmp_path):
    out = tmp_path / "adv.jsonl"
    run_system("excre", ITEMS[:2], MODELS, SIM, CFG, str(out),
               adversarial=True, log=lambda *_: None)
    run_system("excre", ITEMS[:5], MODELS, SIM, CFG, str(out),
               adversarial=True, log=lambda *_: None)
    sab = {r["id"]: r["saboteur"]["model"] for r in read_jsonl(str(out))}
    assert sab == {f"t-{i}": MODELS[i % 3].name for i in range(5)}


def test_unavailable_model_leaves_item_pending(tmp_path):
    out = tmp_path / "cot.jsonl"
    with pytest.raises(ModelUnavailable):
        run_system("cot", ITEMS, [DeadModel("gone")], SIM, CFG, str(out),
                   log=lambda *_: None)
    assert not out.exists()


def test_stops_when_time_is_up(tmp_path):
    out = tmp_path / "cot.jsonl"
    run_system("cot", ITEMS, MODELS, SIM, CFG, str(out),
               stop_at=time.time() - 1, log=lambda *_: None)
    assert not out.exists()


def test_models_needed():
    assert models_needed("cot:m2", MODELS) == {"m2"}
    assert models_needed("sc", MODELS) == {"m1"}
    assert models_needed("mad", MODELS) == {"m1", "m2", "m3"}


def test_variants_and_same_model_group(tmp_path):
    quiet = {"log": lambda *_: None}
    run_system("excre_bare", ITEMS[:2], MODELS, SIM, CFG,
               str(tmp_path / "bare.jsonl"), **quiet)
    run_system("excre_same:m2", ITEMS[:2], MODELS, SIM, CFG,
               str(tmp_path / "same.jsonl"), **quiet)
    bare = read_jsonl(str(tmp_path / "bare.jsonl"))[0]
    assert not any(t.get("devils_advocate") for t in bare["trail"])
    same = read_jsonl(str(tmp_path / "same.jsonl"))[0]
    assert set(same["per_model"]) == {"m2#0", "m2#1", "m2#2"}
    assert models_needed("excre_same:m2", MODELS) == {"m2"}


def test_debate_keeps_rounds_and_takes_a_saboteur(tmp_path):
    out = tmp_path / "mad_adv.jsonl"
    run_system("mad", ITEMS[:3], MODELS, SIM, CFG, str(out),
               adversarial=True, log=lambda *_: None)
    recs = read_jsonl(str(out))
    assert [r["saboteur"]["model"] for r in recs] == ["m1", "m2", "m3"]
    rounds = {t["round"] for t in recs[0]["trail"]}
    assert rounds == set(range(CFG["excre"]["rounds"] + 1))
    assert recs[0]["system"] == "mad_adv"


def test_steps_first_variant_only_reorders_the_schema(tmp_path):
    from excre import prompts
    # the run in runs/v3 is frozen on this hash; the old prompts must not move
    assert prompts.fingerprint() == "4a59f8a0125c253b"
    seen = []

    class Spy(MockModel):
        def chat(self, messages, **kw):
            seen.append(messages[-1]["content"])
            return super().chat(messages, **kw)

    spies = [Spy(m.name, m.persona) for m in MODELS]
    run_system("excre_stepsfirst", ITEMS[:1], spies, SIM, CFG,
               str(tmp_path / "sf.jsonl"), log=lambda *_: None)
    rec = read_jsonl(str(tmp_path / "sf.jsonl"))[0]
    assert rec["system"] == "excre_stepsfirst" and rec["answer"]
    assert seen and all(prompts.SCHEMA_STEPS_FIRST in p for p in seen)
    assert prompts.SCHEMA_STEPS_FIRST.find('"steps"') < prompts.SCHEMA_STEPS_FIRST.find('"answer"')
    assert (prompts.SCHEMA_SPEC.replace(" ", "").replace("\n", "").count('"')
            == prompts.SCHEMA_STEPS_FIRST.replace(" ", "").replace("\n", "").count('"'))

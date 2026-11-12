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

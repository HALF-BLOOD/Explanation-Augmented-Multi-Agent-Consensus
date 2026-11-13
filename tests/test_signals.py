from excre.cara import cara_group, cara_pair
from excre.engine import run_excre
from excre.signals import debate_rounds, excre_signals, pair_scores, plurality
from excre.baselines import run_mad
from test_engine_offline import CFG, ITEM, MODELS, SIM


def test_signals_from_a_sabotaged_run():
    sab = {"model": "m2", "target": "999"}
    rec = run_excre(ITEM, MODELS, SIM, CFG, saboteur=sab)
    row = excre_signals(rec, ITEM, SIM, CFG)
    assert len(row["per_round"]) == rec["rounds_run"] + 1
    assert row["outlier"] in {"m1", "m2", "m3"}
    assert row["saboteur"] == "m2"
    assert abs(row["trust"] - rec["trust"]) < 1e-9
    assert abs(row["induced"] - (row["imrc_coal"] - row["imrc_coal_r0"])) < 1e-9
    assert len(pair_scores(rec, ITEM, SIM, CFG)) == 3


def test_debate_rounds_and_plurality():
    rec = run_mad(ITEM, MODELS, CFG)
    assert len(debate_rounds(rec, ITEM)) == CFG["excre"]["rounds"] + 1
    assert plurality(["7", "8", "8"], str) == "8"
    assert plurality(["7", "8", "9"], str) == "7"


class TableSim:
    # the worked example from the CARA notes: A has 2 steps, B has 3
    grid = {("a1", "b1"): 0.9, ("a1", "b2"): 0.3, ("a1", "b3"): 0.2,
            ("a2", "b1"): 0.4, ("a2", "b2"): 0.8, ("a2", "b3"): 0.5}

    def sim(self, x, y):
        return self.grid[x, y]


class OneClash:
    def probs(self, pairs):
        return [0.95 if set(p) == {"a2", "b3"} else 0.05 for p in pairs]


def _path(*claims):
    return {"steps": [{"claim": c} for c in claims]}


def test_cara_matches_the_worked_example():
    a, b = _path("a1", "a2"), _path("b1", "b2", "b3")
    raw, clash = cara_pair(a, b, TableSim(), OneClash())
    assert abs(raw - (0.85 + (0.9 + 0.8 + 0.2) / 3) / 2) < 1e-9
    assert clash == 0.0
    assert abs(cara_group([a, b], TableSim(), OneClash()) - (raw + 1) / 2) < 1e-9

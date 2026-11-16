import time

import kaggle_run as kr
from excre.data import read_jsonl
from excre.llm import ModelUnavailable
from test_engine_offline import CFG, MODELS, SIM


def make_data(n=4):
    return {ds: [{"id": f"{ds}-{i}", "dataset": ds, "format": "numeric",
                  "question": f"Add {i} and {i + 3}.", "choices": None,
                  "gold": str(2 * i + 3), "meta": {}} for i in range(n)]
            for ds in ("a", "b")}


def make_plan(tmp_path):
    return {"out": str(tmp_path), "stages": [
        {"name": "core", "n": 3, "datasets": ["a", "b"],
         "systems": ["cot:m1", "excre"]},
        {"name": "side", "n": 1, "datasets": ["b"], "systems": ["excre_adv"]}]}


def session(plan, data, fake, monkeypatch):
    calls = []

    def run_item(system, k, item, models, simfn, cfg, adversarial=False):
        job = system + ("_adv" if adversarial else "")
        calls.append((item["id"], job))
        return fake(job, k, item)

    monkeypatch.setattr(kr, "run_item", run_item)
    benched = {}
    stopped = kr.work(plan, data, MODELS, SIM, CFG, {}, time.time() + 60,
                      benched, lambda: None)
    return calls, stopped


def ok(job, k, item):
    return {"id": item["id"], "answer": "1", "correct": True}


def test_one_question_of_every_dataset_at_a_time(tmp_path, monkeypatch):
    calls, stopped = session(make_plan(tmp_path), make_data(), ok, monkeypatch)
    assert stopped is None
    assert calls[:7] == [("a-0", "cot:m1"), ("a-0", "excre"),
                         ("b-0", "cot:m1"), ("b-0", "excre"), ("b-0", "excre_adv"),
                         ("a-1", "cot:m1"), ("a-1", "excre")]
    assert len(calls) == 13
    assert ("b-1", "excre_adv") not in calls


def test_benched_model_finishes_the_question_then_stops(tmp_path, monkeypatch):
    plan, data = make_plan(tmp_path), make_data()

    def flaky(job, k, item):
        if job == "excre" and k == 1:
            raise ModelUnavailable("m2", "daily quota used up")
        return ok(job, k, item)

    calls, stopped = session(plan, data, flaky, monkeypatch)
    assert stopped == "question 2 waiting on m2"
    assert calls[-2:] == [("a-1", "excre"), ("b-1", "cot:m1")]

    calls, stopped = session(plan, data, ok, monkeypatch)
    assert stopped is None
    assert calls[0] == ("a-1", "excre")
    assert len(calls) == 6


def test_crashing_item_gets_two_tries_then_is_left_out(tmp_path, monkeypatch):
    plan, data = make_plan(tmp_path), make_data()

    def broken(job, k, item):
        if item["id"] == "a-0" and job == "cot:m1":
            return {"id": item["id"], "error": "Traceback\nValueError: bad"}
        return ok(job, k, item)

    first, _ = session(plan, data, broken, monkeypatch)
    second, _ = session(plan, data, broken, monkeypatch)
    third, _ = session(plan, data, broken, monkeypatch)
    assert first.count(("a-0", "cot:m1")) == 1
    assert second == [("a-0", "cot:m1")]
    assert third == []
    assert kr.tally(plan, data, {})[1] == {"a": 3, "b": 3}


def test_real_systems_write_one_file_per_dataset_and_system(tmp_path):
    plan = {"out": str(tmp_path), "stages": [
        {"name": "core", "n": 2, "datasets": ["a", "b"],
         "systems": ["cot:m2", "excre"]}]}
    data = make_data(2)
    book = {}
    kr.work(plan, data, MODELS, SIM, CFG, book, time.time() + 60, {},
            lambda: None)
    recs = read_jsonl(str(tmp_path / "b" / "cot_m2.jsonl"))
    assert [r["id"] for r in recs] == ["b-0", "b-1"]
    assert kr.records(book) == 8
    counts, rows = kr.tally(plan, data, {})
    assert rows == {"a": 2, "b": 2}
    assert counts["core", "a", "excre"][0] == 2


def test_sample_grows_without_touching_the_questions_already_drawn(tmp_path,
                                                                   monkeypatch):
    import random
    pool = [{"dataset": "a", "format": "numeric", "question": f"q{i}",
             "choices": None, "gold": str(i), "meta": {}} for i in range(50)]
    seen = []

    def fake_hf(name, cfg, n, seed, revision=None):
        seen.append(revision)
        items = [dict(it) for it in pool]
        random.Random(seed).shuffle(items)
        for i, it in enumerate(items[:n]):
            it["id"] = f"a-{i:04d}"
        return items[:n], {"revision": revision or "abc", "drawn": n}

    monkeypatch.setattr(kr, "load_hf", fake_hf)
    first = kr.load_items("a", 5, str(tmp_path))
    assert kr.load_items("a", 5, str(tmp_path)) == first
    more = kr.load_items("a", 12, str(tmp_path))
    assert more[:5] == first and len(more) == 12
    assert seen == [None, "abc"]

    pool.reverse()
    try:
        kr.load_items("a", 20, str(tmp_path))
        raise AssertionError("a changed draw should not be saved")
    except SystemExit:
        pass
    assert kr.load_items("a", 12, str(tmp_path)) == more

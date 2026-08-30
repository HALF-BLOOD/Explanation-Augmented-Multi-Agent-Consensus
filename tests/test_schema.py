import json

from excre.schema import parse_loose_json, parse_path

GOOD = {
    "answer": "42", "confidence": 0.8,
    "steps": [
        {"id": 1, "claim": "add the two groups", "evidence": "7+4=11 trays",
         "weight": 0.6, "depends_on": []},
        {"id": 2, "claim": "multiply by rolls per tray",
         "evidence": "11*12=132", "weight": 0.4, "depends_on": [1]},
    ],
    "considered": [{"answer": "132", "reason_rejected": "forgot the 15 kept"}],
}


def test_clean_json_parses():
    p = parse_path(json.dumps(GOOD))
    assert p["parsed"]
    assert p["answer"] == "42"
    assert len(p["steps"]) == 2
    assert p["considered"][0]["answer"] == "132"


def test_weights_renormalised():
    obj = dict(GOOD)
    obj["steps"] = [dict(s, weight=5) for s in GOOD["steps"]]
    p = parse_path(json.dumps(obj))
    assert abs(sum(s["weight"] for s in p["steps"]) - 1.0) < 1e-9


def test_fenced_and_surrounded():
    text = "Sure, here you go:\n```json\n" + json.dumps(GOOD) + "\n```\nHope that helps!"
    assert parse_path(text)["parsed"]


def test_trailing_comma_repaired():
    text = '{"answer": "7", "confidence": 0.5, "steps": [{"claim": "x", "evidence": "y", "weight": 1.0,},],}'
    p = parse_path(text)
    assert p["parsed"]
    assert p["answer"] == "7"


def test_steps_as_strings():
    text = '{"answer": "9", "confidence": 0.4, "steps": ["first do a", "then b"]}'
    p = parse_path(text)
    assert p["parsed"]
    assert p["steps"][0]["claim"] == "first do a"


def test_garbage_falls_back():
    p = parse_path("I refuse to answer in JSON. The answer is clearly 12.")
    assert not p["parsed"]
    assert p["steps"]


def test_final_answer_recovered_in_fallback():
    p = parse_path("blah blah\nFinal answer: 88")
    assert p["answer"].startswith("88")


def test_empty_input():
    p = parse_path("")
    assert not p["parsed"]
    assert p["steps"] == []


def test_loose_json_helper():
    assert parse_loose_json('noise {"a": 1} noise') == {"a": 1}
    assert parse_loose_json("no json here") is None

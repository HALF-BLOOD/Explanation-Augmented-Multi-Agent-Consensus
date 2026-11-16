from excre.data import _arc_challenge, _truthfulqa, is_correct, normalise_letter


def test_truthfulqa_gold_follows_the_best_answer():
    rows = [{"Question": f"q{i}", "Best Answer": "right",
             "Incorrect Answers": "w1; w2;w3 ; ", "Type": "Adversarial",
             "Category": "Misconceptions"} for i in range(20)]
    items = _truthfulqa(rows)
    for it in items:
        assert len(it["choices"]) == 4
        assert it["choices"][ord(it["gold"]) - 65] == "right"
    assert len({it["gold"] for it in items}) > 1


def test_arc_numeric_labels_become_letters():
    row = {"id": "x", "question": "q",
           "choices": {"text": ["a", "b", "c"], "label": ["1", "2", "3"]},
           "answerKey": "3"}
    assert _arc_challenge([row])[0]["gold"] == "C"


def test_letters_past_j():
    assert normalise_letter("(L)") == "L"
    assert normalise_letter("M) the last one") == "M"
    item = {"format": "letter", "gold": "K"}
    assert is_correct(item, "K")
    assert not is_correct(item, "J")

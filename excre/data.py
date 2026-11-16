"""Dataset utilities, normalization routines, and benchmark loaders."""

import json
import os
import random
import re
from fractions import Fraction


def read_jsonl(path):
    items = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def append_jsonl(path, obj):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


# Answer normalization

_num_clean = re.compile(r"[,$\s]|(?:\\!)")


def normalise_numeric(text):
    text = str(text).strip()
    text = _num_clean.sub("", text).rstrip("%").rstrip(".")
    m = re.search(r"-?\d+(?:\.\d+)?(?:/\d+)?", text)
    if not m:
        return text.lower()
    tok = m.group(0)
    try:
        val = float(Fraction(tok)) if "/" in tok else float(tok)
    except (ValueError, ZeroDivisionError):
        return tok
    return str(int(val)) if val == int(val) else f"{val:.4f}".rstrip("0")


def normalise_letter(text):
    # truthfulqa questions have up to 13 options, so letters run past J
    text = str(text).strip()
    m = re.match(r"^\(?([A-Za-z])\)?[.:)\s]", text + " ")
    if m:
        return m.group(1).upper()
    m = re.search(r"\(([A-Za-z])\)", text)
    if m:
        return m.group(1).upper()
    return text[:1].upper() if text[:1].isalpha() and len(text) <= 2 else text.lower()


def normalise_yesno(text):
    t = str(text).strip().lower().rstrip(".")
    if t in ("yes", "true", "y"):
        return "yes"
    if t in ("no", "false", "n"):
        return "no"
    if t.startswith("yes"):
        return "yes"
    if t.startswith("no"):
        return "no"
    return t


def make_normaliser(fmt):
    return {
        "numeric": normalise_numeric,
        "letter": normalise_letter,
        "yesno": normalise_yesno,
    }.get(fmt, lambda t: str(t).strip().lower())


def is_correct(item, answer):
    norm = make_normaliser(item["format"])
    return norm(answer) == norm(item["gold"])


def extract_final_answer(text):
    """Extract final answer string from model output text."""
    if not text:
        return ""
    m = None
    for m in re.finditer(r"final answer\s*\**\s*[:=]", text, re.IGNORECASE):
        pass
    if m:
        # models like to bold the label and put the answer on the next line
        for line in text[m.end():].splitlines():
            line = re.sub(r"[*`]+", "", line).strip()
            if line:
                return line
    tail = text[-300:]
    nums = re.findall(r"-?\d[\d,]*(?:\.\d+)?", tail)
    if nums:
        return nums[-1]
    letters = re.findall(r"\(([A-Z])\)", tail)
    return letters[-1] if letters else tail.strip()[-40:]


# Benchmark loaders: (repo, config, split) of the official Hugging Face release

SOURCES = {
    "gsm8k": ("openai/gsm8k", "main", "test"),
    "strategyqa": ("ChilleD/StrategyQA", None, "test"),
    "truthfulqa": ("domenicrosati/TruthfulQA", None, "train"),
    "arc_challenge": ("allenai/ai2_arc", "ARC-Challenge", "test"),
    "mmlu": ("cais/mmlu", "all", "test"),
}


def load_hf(name, subset_cfg, n, seed, revision=None):
    """Shuffle the whole split with `seed` and keep the first n items.

    Returns the items and where they came from, including the dataset
    revision, so the exact draw can be repeated or extended later: the same
    seed and revision with a bigger n gives the same first items.
    """
    from datasets import load_dataset
    from huggingface_hub import HfApi

    repo, config, split = SOURCES[name]
    # split=train on gsm8k gives a dev slice disjoint from the test items
    split = subset_cfg.get("split", split)
    revision = revision or HfApi().dataset_info(repo).sha
    rows = load_dataset(repo, config, split=split, revision=revision)
    items = _LOADERS[name](rows)
    random.Random(seed).shuffle(items)
    picked = items[:n]
    for i, it in enumerate(picked):
        it["id"] = f"{name}-{i:04d}"
    source = {"repo": repo, "config": config, "split": split,
              "revision": revision, "rows": len(items), "drawn": len(picked),
              "seed": seed}
    return picked, source


def _gsm8k(rows):
    return [{"dataset": "gsm8k", "format": "numeric",
             "question": r["question"], "choices": None,
             "gold": r["answer"].split("####")[-1].strip(), "meta": {}}
            for r in rows]


def _strategyqa(rows):
    return [{"dataset": "strategyqa", "format": "yesno",
             "question": r["question"], "choices": None,
             "gold": "yes" if r["answer"] else "no",
             "meta": {"qid": r["qid"]}}
            for r in rows]


def _truthfulqa(rows):
    # the csv release has one best answer and a list of incorrect ones, the
    # same material the mc1 task is built from; options are shuffled so the
    # right one isn't always (A)
    rng = random.Random(20049123)
    out = []
    for r in rows:
        wrong = [a.strip() for a in r["Incorrect Answers"].split(";") if a.strip()]
        choices = [r["Best Answer"].strip()] + wrong
        order = list(range(len(choices)))
        rng.shuffle(order)
        out.append({"dataset": "truthfulqa", "format": "letter",
                    "question": r["Question"],
                    "choices": [choices[i] for i in order],
                    "gold": chr(65 + order.index(0)),
                    "meta": {"type": r["Type"], "category": r["Category"]}})
    return out


def _arc_challenge(rows):
    # a few questions are labelled 1-4 instead of A-D; letters go by position
    return [{"dataset": "arc_challenge", "format": "letter",
             "question": r["question"],
             "choices": list(r["choices"]["text"]),
             "gold": chr(65 + list(r["choices"]["label"]).index(r["answerKey"])),
             "meta": {"id": r["id"]}}
            for r in rows]


def _mmlu(rows):
    return [{"dataset": "mmlu", "format": "letter",
             "question": r["question"], "choices": list(r["choices"]),
             "gold": chr(65 + int(r["answer"])),
             "meta": {"subject": r["subject"]}}
            for r in rows]


_LOADERS = {
    "gsm8k": _gsm8k,
    "strategyqa": _strategyqa,
    "truthfulqa": _truthfulqa,
    "arc_challenge": _arc_challenge,
    "mmlu": _mmlu,
}

AVAILABLE_DATASETS = sorted(_LOADERS)

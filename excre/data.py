"""Dataset utilities, normalization routines, and benchmark loaders."""

import json
import os
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
    text = str(text).strip()
    m = re.match(r"^\(?([A-Ja-j])\)?[.:)\s]", text + " ")
    if m:
        return m.group(1).upper()
    m = re.search(r"\(([A-Ja-j])\)", text)
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
    for m in re.finditer(r"final answer\s*[:=]\s*(.+)", text, re.IGNORECASE):
        pass
    if m:
        return m.group(1).strip().splitlines()[0]
    tail = text[-300:]
    nums = re.findall(r"-?\d[\d,]*(?:\.\d+)?", tail)
    if nums:
        return nums[-1]
    letters = re.findall(r"\(([A-J])\)", tail)
    return letters[-1] if letters else tail.strip()[-40:]


# Benchmark dataset loaders

def load_hf(name, subset_cfg, n, seed):
    import random
    from datasets import load_dataset

    rng = random.Random(seed)
    make = _LOADERS[name]
    items = make(load_dataset, subset_cfg)
    rng.shuffle(items)
    picked = items[:n]
    for i, it in enumerate(picked):
        it["id"] = f"{name}-{i:04d}"
    return picked


def _gsm8k(load_dataset, cfg):
    # split=train gives a disjoint dev slice for prompt/threshold tuning,
    # so nothing is ever tuned on the test items
    ds = load_dataset("openai/gsm8k", "main",
                      split=cfg.get("split", "test"))
    out = []
    for row in ds:
        gold = row["answer"].split("####")[-1].strip()
        out.append({"dataset": "gsm8k", "format": "numeric",
                    "question": row["question"], "choices": None,
                    "gold": gold, "meta": {}})
    return out


def _mmlu(load_dataset, cfg):
    subjects = cfg.get("mmlu_subjects", [
        "high_school_mathematics", "philosophy",
        "clinical_knowledge", "global_facts"])
    out = []
    for sub in subjects:
        ds = load_dataset("cais/mmlu", sub, split="test")
        for row in ds:
            out.append({"dataset": "mmlu", "format": "letter",
                        "question": row["question"],
                        "choices": list(row["choices"]),
                        "gold": chr(65 + int(row["answer"])),
                        "meta": {"subject": sub}})
    return out


def _strategyqa(load_dataset, cfg):
    ds = load_dataset("ChilleD/StrategyQA", split="test")
    return [{"dataset": "strategyqa", "format": "yesno",
             "question": row["question"], "choices": None,
             "gold": "yes" if row["answer"] else "no", "meta": {}}
            for row in ds]


def _truthfulqa(load_dataset, cfg):
    import random
    ds = load_dataset("truthful_qa", "multiple_choice", split="validation")
    rng = random.Random(20049123)
    out = []
    for row in ds:
        choices = list(row["mc1_targets"]["choices"])
        labels = list(row["mc1_targets"]["labels"])
        order = list(range(len(choices)))
        rng.shuffle(order)
        shuffled = [choices[i] for i in order]
        gold_idx = order.index(labels.index(1))
        out.append({"dataset": "truthfulqa", "format": "letter",
                    "question": row["question"], "choices": shuffled,
                    "gold": chr(65 + gold_idx), "meta": {}})
    return out


def _medqa(load_dataset, cfg):
    ds = load_dataset("GBaker/MedQA-USMLE-4-options", split="test")
    out = []
    for row in ds:
        opts = row["options"]
        keys = sorted(opts.keys())
        out.append({"dataset": "medqa", "format": "letter",
                    "question": row["question"],
                    "choices": [opts[k] for k in keys],
                    "gold": row["answer_idx"], "meta": {}})
    return out


_LOADERS = {
    "gsm8k": _gsm8k,
    "mmlu": _mmlu,
    "strategyqa": _strategyqa,
    "truthfulqa": _truthfulqa,
    "medqa": _medqa,
}

AVAILABLE_DATASETS = sorted(_LOADERS)

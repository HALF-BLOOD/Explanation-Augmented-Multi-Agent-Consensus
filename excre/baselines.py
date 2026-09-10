"""Baseline multi-agent and single-agent reasoning methods.

Includes standard Chain-of-Thought (CoT), Self-Consistency (SC), Multi-Agent
Debate (MAD), ReConcile-style discussion, and centralized LLM-as-Judge synthesis.
"""

from collections import Counter

from . import prompts, schema
from .data import extract_final_answer, make_normaliser


def _chat(model, prompt, gen, tokens, system=None):
    messages = ([{"role": "system", "content": system}] if system else [])
    messages.append({"role": "user", "content": prompt})
    text, usage = model.chat(messages, **gen)
    tokens["prompt"] += usage.get("prompt_tokens", 0)
    tokens["completion"] += usage.get("completion_tokens", 0)
    return text


def run_cot(item, model, cfg):
    gen = {"temperature": cfg["excre"].get("temperature", 0.3),
           "max_tokens": cfg["excre"].get("max_tokens", 900)}
    tokens = {"prompt": 0, "completion": 0}
    fmt = prompts.format_instruction(item)
    text = _chat(model, prompts.cot(item["question"], fmt), gen, tokens)
    return {"system": f"cot_{model.name}", "id": item["id"],
            "answer": extract_final_answer(text), "signal": 0.5,
            "tokens": tokens, "raw": text}


def run_self_consistency(item, model, cfg):
    sc = cfg.get("sc", {})
    k = sc.get("k", 5)
    gen = {"temperature": sc.get("temperature", 0.7),
           "max_tokens": cfg["excre"].get("max_tokens", 900)}
    tokens = {"prompt": 0, "completion": 0}
    fmt = prompts.format_instruction(item)
    norm = make_normaliser(item["format"])

    votes = Counter()
    raw_answers = []
    for i in range(k):
        # Vary generation seed per sample
        text, usage = model.chat(
            [{"role": "user",
              "content": prompts.cot(item["question"], fmt)}],
            temperature=gen["temperature"], max_tokens=gen["max_tokens"],
            seed=i)
        tokens["prompt"] += usage.get("prompt_tokens", 0)
        tokens["completion"] += usage.get("completion_tokens", 0)
        ans = extract_final_answer(text)
        raw_answers.append(ans)
        votes[norm(ans)] += 1

    best, count = votes.most_common(1)[0]
    return {"system": f"sc_{model.name}", "id": item["id"], "answer": best,
            "signal": count / k, "samples": raw_answers, "tokens": tokens}


def run_mad(item, models, cfg, rounds=None):
    ex = cfg["excre"]
    gen = {"temperature": ex.get("temperature", 0.3),
           "max_tokens": ex.get("max_tokens", 900)}
    rounds = rounds if rounds is not None else ex.get("rounds", 3)
    tokens = {"prompt": 0, "completion": 0}
    fmt = prompts.format_instruction(item)
    norm = make_normaliser(item["format"])

    texts = {m.name: _chat(m, prompts.mad_initial(item["question"], fmt),
                           gen, tokens) for m in models}
    for _ in range(rounds):
        texts = {m.name: _chat(
            m, prompts.mad_revision(item["question"], fmt, texts[m.name],
                                    [texts[p.name] for p in models
                                     if p.name != m.name]),
            gen, tokens) for m in models}

    votes = Counter(norm(extract_final_answer(t)) for t in texts.values())
    best, count = votes.most_common(1)[0]
    return {"system": "mad", "id": item["id"], "answer": best,
            "signal": count / len(models),
            "per_model": {n: extract_final_answer(t) for n, t in texts.items()},
            "tokens": tokens}


def _reconcile_parse(text):
    obj = schema.parse_loose_json(text) or {}
    conf = obj.get("confidence", 0.5)
    try:
        conf = max(0.0, min(1.0, float(conf)))
    except (TypeError, ValueError):
        conf = 0.5
    return {"answer": str(obj.get("answer", "")).strip()
            or extract_final_answer(text),
            "explanation": str(obj.get("explanation", ""))[:600],
            "confidence": conf}


def run_reconcile(item, models, cfg, rounds=None):
    ex = cfg["excre"]
    gen = {"temperature": ex.get("temperature", 0.3),
           "max_tokens": ex.get("max_tokens", 900)}
    rounds = rounds if rounds is not None else ex.get("rounds", 3)
    tokens = {"prompt": 0, "completion": 0}
    fmt = prompts.format_instruction(item)
    norm = make_normaliser(item["format"])

    state = {m.name: _reconcile_parse(
        _chat(m, prompts.reconcile_initial(item["question"], fmt), gen,
              tokens)) for m in models}

    for _ in range(rounds):
        groups = {}
        for name, s in state.items():
            groups.setdefault(norm(s["answer"]), []).append((name, s))
        summary = []
        for ans, members in groups.items():
            summary.append(f"Answer \"{members[0][1]['answer']}\" "
                           f"({len(members)} model(s)):")
            for name, s in members:
                summary.append(f"  - {name} (confidence "
                               f"{s['confidence']:.2f}): {s['explanation']}")
        prompt = prompts.reconcile_discussion(item["question"], fmt,
                                              "\n".join(summary))
        state = {m.name: _reconcile_parse(_chat(m, prompt, gen, tokens))
                 for m in models}

    # Confidence-weighted margin
    weights = Counter()
    for s in state.values():
        weights[norm(s["answer"])] += 0.5 + 0.5 * s["confidence"]
    best = max(weights, key=weights.get)
    margin = weights[best] / sum(weights.values())
    return {"system": "reconcile", "id": item["id"], "answer": best,
            "signal": margin,
            "per_model": {n: s["answer"] for n, s in state.items()},
            "tokens": tokens}


def run_judge(item, models, cfg):
    ex = cfg["excre"]
    gen = {"temperature": ex.get("temperature", 0.3),
           "max_tokens": ex.get("max_tokens", 900)}
    tokens = {"prompt": 0, "completion": 0}
    fmt = prompts.format_instruction(item)

    displays = []
    for m in models:
        text = _chat(m, prompts.cot(item["question"], fmt), gen, tokens)
        displays.append(f"[{m.name}]\n{text}")

    judge_name = cfg.get("judge", {}).get("model") or models[0].name
    judge = next((m for m in models if m.name == judge_name), models[0])
    verdict = _chat(judge, prompts.judge_synthesis(item["question"], fmt,
                                                   displays), gen, tokens)
    return {"system": "judge", "id": item["id"],
            "answer": extract_final_answer(verdict), "signal": 0.5,
            "judge": judge.name, "tokens": tokens}

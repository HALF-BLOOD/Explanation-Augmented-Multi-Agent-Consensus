"""Baseline multi-agent and single-agent reasoning methods.

Includes standard Chain-of-Thought (CoT), Self-Consistency (SC), Multi-Agent
Debate (MAD), ReConcile-style discussion, and centralized LLM-as-Judge synthesis.
"""

from collections import Counter

from . import prompts, schema
from .data import extract_final_answer, make_normaliser


def _chat(model, prompt, gen, tokens, system=None, seed=None):
    messages = ([{"role": "system", "content": system}] if system else [])
    messages.append({"role": "user", "content": prompt})
    text, usage = model.chat(messages, seed=seed, **gen)
    tokens["prompt"] += usage.get("prompt_tokens", 0)
    tokens["completion"] += usage.get("completion_tokens", 0)
    if usage.get("finish") == "length":
        tokens["cut"] = tokens.get("cut", 0) + 1
    return text


def _solve(model, prompt, gen, tokens, system=None, seed=None):
    # one retry when the answer line is missing, to match the single repair
    # attempt the schema gets in the excre loop
    text = _chat(model, prompt, gen, tokens, system, seed)
    if "final answer" not in text.lower():
        again = _chat(model, prompt + prompts.RETRY_FINAL, gen, tokens,
                      system, seed)
        if "final answer" in again.lower():
            return again
    return text


def run_cot(item, model, cfg):
    gen = {"temperature": cfg["excre"].get("temperature", 0.3),
           "max_tokens": cfg["excre"].get("max_tokens", 900)}
    tokens = {"prompt": 0, "completion": 0}
    fmt = prompts.format_instruction(item)
    text = _solve(model, prompts.cot(item["question"], fmt), gen, tokens)
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
    raw_answers, raws = [], []
    for i in range(k):
        text = _solve(model, prompts.cot(item["question"], fmt), gen,
                      tokens, seed=i)
        ans = extract_final_answer(text)
        raw_answers.append(ans)
        raws.append(text)
        votes[norm(ans)] += 1

    best, count = votes.most_common(1)[0]
    return {"system": f"sc_{model.name}", "id": item["id"], "answer": best,
            "signal": count / k, "samples": raw_answers, "raws": raws,
            "tokens": tokens}


def run_mad(item, models, cfg, rounds=None, saboteur=None):
    ex = cfg["excre"]
    gen = {"temperature": ex.get("temperature", 0.3),
           "max_tokens": ex.get("max_tokens", 900)}
    rounds = rounds if rounds is not None else ex.get("rounds", 3)
    tokens = {"prompt": 0, "completion": 0}
    fmt = prompts.format_instruction(item)
    norm = make_normaliser(item["format"])

    def system_for(m):
        if saboteur and m.name == saboteur["model"]:
            return prompts.SABOTEUR_SYSTEM.format(target=saboteur["target"])
        return None

    trail = []

    def keep(r, texts):
        trail.extend({"round": r, "model": n, "text": t,
                      "answer": extract_final_answer(t)}
                     for n, t in texts.items())

    texts = {m.name: _solve(m, prompts.mad_initial(item["question"], fmt),
                            gen, tokens, system_for(m)) for m in models}
    keep(0, texts)
    for r in range(1, rounds + 1):
        texts = {m.name: _solve(
            m, prompts.mad_revision(item["question"], fmt, texts[m.name],
                                    [texts[p.name] for p in models
                                     if p.name != m.name]),
            gen, tokens, system_for(m)) for m in models}
        keep(r, texts)

    votes = Counter(norm(extract_final_answer(t)) for t in texts.values())
    best, count = votes.most_common(1)[0]
    return {"system": "mad", "id": item["id"], "answer": best,
            "signal": count / len(models),
            "per_model": {n: extract_final_answer(t) for n, t in texts.items()},
            "tokens": tokens, "saboteur": saboteur, "trail": trail}


def _reconcile_turn(model, prompt, gen, tokens):
    text = _chat(model, prompt, gen, tokens)
    if schema.parse_loose_json(text) is None:
        again = _chat(model, prompt + prompts.RETRY_SCHEMA, gen, tokens)
        if schema.parse_loose_json(again) is not None:
            text = again
    return _reconcile_parse(text)


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

    state = {m.name: _reconcile_turn(
        m, prompts.reconcile_initial(item["question"], fmt), gen, tokens)
        for m in models}
    trail = [dict(s, round=0, model=n) for n, s in state.items()]

    for r in range(1, rounds + 1):
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
        state = {m.name: _reconcile_turn(m, prompt, gen, tokens)
                 for m in models}
        trail.extend(dict(s, round=r, model=n) for n, s in state.items())

    # Confidence-weighted margin
    weights = Counter()
    for s in state.values():
        weights[norm(s["answer"])] += 0.5 + 0.5 * s["confidence"]
    best = max(weights, key=weights.get)
    margin = weights[best] / sum(weights.values())
    return {"system": "reconcile", "id": item["id"], "answer": best,
            "signal": margin,
            "per_model": {n: s["answer"] for n, s in state.items()},
            "tokens": tokens, "trail": trail}


def run_judge(item, models, cfg):
    ex = cfg["excre"]
    gen = {"temperature": ex.get("temperature", 0.3),
           "max_tokens": ex.get("max_tokens", 900)}
    tokens = {"prompt": 0, "completion": 0}
    fmt = prompts.format_instruction(item)

    displays, candidates = [], {}
    for m in models:
        text = _solve(m, prompts.cot(item["question"], fmt), gen, tokens)
        displays.append(f"[{m.name}]\n{text}")
        candidates[m.name] = extract_final_answer(text)

    judge_name = cfg.get("judge", {}).get("model") or models[0].name
    judge = next((m for m in models if m.name == judge_name), models[0])
    verdict = _solve(judge, prompts.judge_synthesis(item["question"], fmt,
                                                    displays), gen, tokens)
    return {"system": "judge", "id": item["id"],
            "answer": extract_final_answer(verdict), "signal": 0.5,
            "judge": judge.name, "candidates": candidates, "raw": verdict,
            "tokens": tokens}

"""Experiment runner with resume capability and per-item checkpointing."""

import json
import os
import time
import traceback

from . import baselines
from .data import append_jsonl, is_correct, make_normaliser, read_jsonl
from .engine import run_excre
from .llm import ModelUnavailable


def done_ids(path):
    # error records don't count as done: a resumed run retries those items
    # (their successful calls come back free from the response cache)
    if not os.path.exists(path):
        return set()
    return {r["id"] for r in read_jsonl(path) if "error" not in r}


def plausible_wrong_answer(item):
    """Generate plausible incorrect answer target for adversarial evaluation."""
    norm = make_normaliser(item["format"])
    gold = norm(item["gold"])
    if item["format"] == "yesno":
        return "No" if gold == "yes" else "Yes"
    if item["format"] == "letter" and item.get("choices"):
        for i in range(len(item["choices"])):
            letter = chr(65 + i)
            if norm(letter) != gold:
                return letter
        return "A"
    if item["format"] == "numeric":
        try:
            v = float(gold)
            wrong = v * 2 + 1 if abs(v) < 1e6 else v + 17
            return str(int(wrong)) if wrong == int(wrong) else str(wrong)
        except ValueError:
            return gold + "0"
    return "none of the above"


def run_system(system, items, models, simfn, cfg, out_path,
               adversarial=False, log=print, stop_at=None, after_item=None):
    done = done_ids(out_path)
    # k is the item's position in the dataset, not in the leftover list, so
    # the saboteur rotation doesn't shift every time a run resumes
    todo = [(k, it) for k, it in enumerate(items) if it["id"] not in done]
    if not todo:
        return
    tag = system + ("_adv" if adversarial else "")
    if done:
        log(f"[{tag}] resuming: {len(done)} done, {len(todo)} to go")

    n_err = 0
    t0 = time.time()
    for j, (k, item) in enumerate(todo):
        if stop_at and time.time() > stop_at:
            log(f"[{tag}] out of time after {j} items")
            return
        try:
            rec = _dispatch(system, item, models, simfn, cfg,
                            adversarial, k)
            rec["correct"] = is_correct(item, rec["answer"])
            rec["gold"] = item["gold"]
            rec["dataset"] = item["dataset"]
        except (KeyboardInterrupt, ModelUnavailable):
            raise
        except Exception:
            n_err += 1
            rec = {"system": system, "id": item["id"], "error":
                   traceback.format_exc(limit=3)}
            log(f"[{tag}] error on {item['id']} "
                f"({n_err} so far)")
        append_jsonl(out_path, rec)
        if after_item:
            after_item()
        if (j + 1) % 10 == 0:
            rate = (j + 1) / max(time.time() - t0, 1e-6)
            log(f"[{tag}] {j + 1}/{len(todo)} ({rate:.2f} items/s)")
    log(f"[{tag}] finished: {len(todo)} items, {n_err} errors -> {out_path}")


def models_needed(system, models):
    if system.startswith(("cot", "sc")):
        prefix = system.split(":", 1)[0]
        return {_pick_model(system, prefix, models).name}
    return {m.name for m in models}


def _dispatch(system, item, models, simfn, cfg, adversarial, k):
    if system == "excre":
        saboteur = None
        if adversarial:
            saboteur = {"model": models[k % len(models)].name,
                        "target": plausible_wrong_answer(item)}
        return run_excre(item, models, simfn, cfg, saboteur=saboteur)
    if system == "mad":
        return baselines.run_mad(item, models, cfg)
    if system == "reconcile":
        return baselines.run_reconcile(item, models, cfg)
    if system == "judge":
        return baselines.run_judge(item, models, cfg)
    if system.startswith("cot"):
        model = _pick_model(system, "cot", models)
        return baselines.run_cot(item, model, cfg)
    if system.startswith("sc"):
        model = _pick_model(system, "sc", models)
        return baselines.run_self_consistency(item, model, cfg)
    raise ValueError(f"unknown system: {system}")


def _pick_model(system, prefix, models):
    # Resolve specific model target if indicated (e.g. "cot:model_name")
    if ":" in system:
        name = system.split(":", 1)[1]
        for m in models:
            if m.name == name:
                return m
        raise ValueError(f"no model named {name}")
    return models[0]

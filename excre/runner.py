"""Experiment runner with resume capability and per-item checkpointing."""

import json
import os
import time
import traceback

from . import baselines
from .data import append_jsonl, is_correct, make_normaliser, read_jsonl
from .engine import run_excre


def _done_ids(path):
    if not os.path.exists(path):
        return set()
    return {r["id"] for r in read_jsonl(path)}


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
               adversarial=False, log=print):
    done = _done_ids(out_path)
    todo = [it for it in items if it["id"] not in done]
    if done:
        log(f"[{system}] resuming: {len(done)} done, {len(todo)} to go")

    n_err = 0
    t0 = time.time()
    for k, item in enumerate(todo):
        try:
            rec = _dispatch(system, item, models, simfn, cfg,
                            adversarial, k)
            rec["correct"] = is_correct(item, rec["answer"])
            rec["gold"] = item["gold"]
            rec["dataset"] = item["dataset"]
        except KeyboardInterrupt:
            raise
        except Exception:
            n_err += 1
            rec = {"system": system, "id": item["id"], "error":
                   traceback.format_exc(limit=3)}
            log(f"[{system}] error on {item['id']} "
                f"({n_err} so far)")
        append_jsonl(out_path, rec)
        if (k + 1) % 10 == 0:
            rate = (k + 1) / max(time.time() - t0, 1e-6)
            log(f"[{system}] {k + 1}/{len(todo)} ({rate:.2f} items/s)")
    log(f"[{system}] finished: {len(todo)} items, {n_err} errors -> {out_path}")


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

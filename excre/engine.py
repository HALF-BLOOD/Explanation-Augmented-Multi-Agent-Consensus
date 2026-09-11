"""Execution engine for Explanation-Augmented Cross-Model Reasoning Exchange (EXCRE).

Implements round-0 independent generation, iterative peer-revision rounds with
anchor conditioning and optional devil's advocacy, convergence checking, and
consensus scoring.
"""

from . import prompts, schema
from .data import make_normaliser
from .imrc import imrc_group
from .trust import (coalition, consensus_answer, fragility, trust_components,
                    trust_score)


def _call(model, user_prompt, system=None, gen=None):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user_prompt})
    text, usage = model.chat(messages, **(gen or {}))
    return text, usage


def _generate_path(model, user_prompt, system, gen, tokens):
    text, usage = _call(model, user_prompt, system, gen)
    tokens["prompt"] += usage.get("prompt_tokens", 0)
    tokens["completion"] += usage.get("completion_tokens", 0)
    path = schema.parse_path(text)
    if not path["parsed"]:
        # Retry with explicit format prompt
        retry_prompt = (user_prompt + "\n\nYour previous reply could not be "
                        "parsed as the required JSON object. Reply with only "
                        "the JSON object this time.")
        text2, usage2 = _call(model, retry_prompt, system, gen)
        tokens["prompt"] += usage2.get("prompt_tokens", 0)
        tokens["completion"] += usage2.get("completion_tokens", 0)
        path2 = schema.parse_path(text2)
        if path2["parsed"]:
            return path2, text2, True
    return path, text, False


def run_excre(item, models, simfn, cfg, saboteur=None):
    """Execute EXCRE on an evaluation item.

    saboteur: None or {"model": <name>, "target": <wrong answer string>}.
    """
    ex = cfg["excre"]
    gen = {"temperature": ex.get("temperature", 0.3),
           "max_tokens": ex.get("max_tokens", 900)}
    imrc_w = (cfg["imrc"]["alpha"], cfg["imrc"]["beta"], cfg["imrc"]["gamma"])
    ev_thr = cfg["imrc"].get("evidence_threshold", 0.5)
    norm = make_normaliser(item["format"])
    fmt = prompts.format_instruction(item)

    def system_for(model):
        if saboteur and model.name == saboteur["model"]:
            return prompts.SABOTEUR_SYSTEM.format(target=saboteur["target"])
        return None

    tokens = {"prompt": 0, "completion": 0}
    trail = []

    # Round 0: independent generation
    current = {}
    round0 = {}
    for m in models:
        path, raw, repaired = _generate_path(
            m, prompts.initial(item["question"], fmt), system_for(m), gen,
            tokens)
        current[m.name] = path
        round0[m.name] = path
        trail.append({"round": 0, "model": m.name, "raw": raw,
                      "path": path, "repaired": repaired})

    prev_imrc = imrc_group(list(current.values()), simfn, imrc_w, ev_thr)["imrc"]
    converged = False
    rounds_run = 0

    # Revision rounds
    for r in range(1, ex.get("rounds", 3) + 1):
        rounds_run = r
        da_index = (r - 1) % len(models) if ex.get("devils_advocate", True) else -1
        prev_answers = {name: norm(p["answer"]) for name, p in current.items()}

        revised = {}
        for idx, m in enumerate(models):
            own = schema.path_to_display(current[m.name], "you, current")
            anchor = (schema.path_to_display(round0[m.name], "you, round 0")
                      if ex.get("anchor", True) else "(anchor disabled)")
            peers = [schema.path_to_display(current[p.name], f"peer {p.name}")
                     for p in models if p.name != m.name]
            prompt = prompts.revision(item["question"], fmt, own, anchor,
                                      peers, devils_advocate=(idx == da_index))
            path, raw, repaired = _generate_path(m, prompt, system_for(m),
                                                 gen, tokens)
            revised[m.name] = path
            trail.append({"round": r, "model": m.name, "raw": raw,
                          "path": path, "repaired": repaired,
                          "devils_advocate": idx == da_index})
        current = revised

        cur_imrc = imrc_group(list(current.values()), simfn, imrc_w, ev_thr)["imrc"]
        stable = all(norm(current[n]["answer"]) == prev_answers[n]
                     for n in current)
        if stable and abs(cur_imrc - prev_imrc) < ex.get("convergence_eps", 0.02):
            converged = True
            break
        prev_imrc = cur_imrc

    # Consensus and trust
    final_paths = list(current.values())
    answer, agreement = consensus_answer(final_paths, norm)
    coal = coalition(final_paths, answer, norm)
    imrc_all = imrc_group(final_paths, simfn, imrc_w, ev_thr)
    imrc_coal = imrc_group(coal, simfn, imrc_w, ev_thr)

    comps = trust_components(coal, imrc_all["imrc"], imrc_coal["imrc"],
                             agreement, converged)
    trust = trust_score(comps, cfg["trust"])

    return {
        "system": "excre",
        "id": item["id"],
        "answer": answer,
        "trust": trust,
        "signal": trust,
        "components": comps,
        "imrc_all": imrc_all,
        "imrc_coalition": imrc_coal,
        "fragility": fragility(agreement, imrc_coal["imrc"]),
        "per_model": {n: {"answer": p["answer"],
                          "confidence": p["confidence"],
                          "parsed": p["parsed"]}
                      for n, p in current.items()},
        "rounds_run": rounds_run,
        "converged": converged,
        "tokens": tokens,
        "saboteur": saboteur,
        "trail": trail,
    }

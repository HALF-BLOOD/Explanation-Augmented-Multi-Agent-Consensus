"""Per-item signals recomputed from stored trails, for the paper analysis."""

from collections import Counter
from itertools import combinations

from .data import make_normaliser
from .imrc import imrc_group, imrc_pair
from .trust import (consensus_answer, fragility, trust_components,
                    trust_score)


def paths_by_round(rec):
    rounds = {}
    for t in rec["trail"]:
        rounds.setdefault(t["round"], {})[t["model"]] = t["path"]
    return [rounds[r] for r in sorted(rounds)]


def excre_signals(rec, item, simfn, cfg, extra=None):
    """Flat dict of everything the analysis needs from one excre record.

    extra: optional {name: fn(paths) -> float} scored on the final coalition,
    e.g. the CARA baseline.
    """
    w = (cfg["imrc"]["alpha"], cfg["imrc"]["beta"], cfg["imrc"]["gamma"])
    thr = cfg["imrc"].get("evidence_threshold", 0.5)
    norm = make_normaliser(item["format"])
    gold = norm(item["gold"])

    rounds = paths_by_round(rec)
    first, last = rounds[0], rounds[-1]
    per_round = []
    for paths in rounds:
        ans, agree = consensus_answer(list(paths.values()), norm)
        per_round.append({
            "correct": ans == gold, "agreement": agree,
            "imrc": imrc_group(list(paths.values()), simfn, w, thr)["imrc"]})

    final = list(last.values())
    answer, agreement = consensus_answer(final, norm)
    members = [n for n, p in last.items() if norm(p["answer"]) == answer]
    coal = [last[n] for n in members]
    imrc_all = imrc_group(final, simfn, w, thr)
    imrc_coal = imrc_group(coal, simfn, w, thr)
    comps = trust_components(coal, imrc_all["imrc"], imrc_coal["imrc"],
                             agreement, rec.get("converged", False))
    # the coalition's congruence before anyone had seen anyone else
    imrc_coal0 = imrc_group([first[n] for n in members], simfn, w, thr)["imrc"]

    # agent whose final path sits furthest from the others
    names = list(last)
    apart = {n: 0.0 for n in names}
    for a, b in combinations(names, 2):
        s = imrc_pair(last[a], last[b], simfn, w, thr)["imrc"]
        apart[a] += s
        apart[b] += s
    outlier = min(names, key=lambda n: apart[n])
    minority = [n for n in names if n not in members]

    sab = rec.get("saboteur") or {}
    row = {
        "id": rec["id"], "dataset": item["dataset"],
        "correct": answer == gold, "correct_r0": per_round[0]["correct"],
        "agreement": agreement, "agreement_r0": per_round[0]["agreement"],
        "confidence": comps["mean_confidence"],
        "imrc_all": imrc_all["imrc"], "imrc_coal": imrc_coal["imrc"],
        "semantic": imrc_coal["semantic"], "structural": imrc_coal["structural"],
        "evidence": imrc_coal["evidence"],
        "imrc_all_r0": per_round[0]["imrc"], "imrc_coal_r0": imrc_coal0,
        "induced": imrc_coal["imrc"] - imrc_coal0,
        "defined": imrc_coal["pairs"] > 0,
        "trust": trust_score(comps, cfg["trust"]),
        "fragility": fragility(agreement, imrc_coal["imrc"], imrc_coal["pairs"]),
        "rounds": rec.get("rounds_run", len(rounds) - 1),
        "converged": bool(rec.get("converged")),
        "tokens": rec["tokens"]["prompt"] + rec["tokens"]["completion"],
        "saboteur": sab.get("model"),
        "sab_won": bool(sab) and answer == norm(sab["target"]),
        "sab_complied": bool(sab) and norm(last[sab["model"]]["answer"]) == norm(sab["target"]),
        "outlier": outlier,
        "minority": minority[0] if len(minority) == 1 else None,
        "per_round": per_round,
    }
    for name, fn in (extra or {}).items():
        row[name] = fn(coal) if len(coal) > 1 else 0.0
    return row


def pair_scores(rec, item, simfn, cfg, extra=None):
    """(same_answer, score...) for every agent pair in the final round."""
    w = (cfg["imrc"]["alpha"], cfg["imrc"]["beta"], cfg["imrc"]["gamma"])
    thr = cfg["imrc"].get("evidence_threshold", 0.5)
    norm = make_normaliser(item["format"])
    last = paths_by_round(rec)[-1]
    out = []
    for a, b in combinations(list(last), 2):
        row = {"same": norm(last[a]["answer"]) == norm(last[b]["answer"]),
               "imrc": imrc_pair(last[a], last[b], simfn, w, thr)["imrc"]}
        for name, fn in (extra or {}).items():
            row[name] = fn([last[a], last[b]])
        out.append(row)
    return out


def debate_rounds(rec, item):
    """Majority answer per round of a free-text debate record."""
    norm = make_normaliser(item["format"])
    gold = norm(item["gold"])
    rounds = {}
    for t in rec.get("trail", []):
        rounds.setdefault(t["round"], []).append(norm(t["answer"]))
    out = []
    for r in sorted(rounds):
        best, count = Counter(rounds[r]).most_common(1)[0]
        out.append({"correct": best == gold, "agreement": count / len(rounds[r])})
    return out


def plurality(answers, norm):
    """Most common normalised answer; ties go to whoever comes first."""
    votes = Counter(norm(a) for a in answers)
    top = max(votes.values())
    return next(norm(a) for a in answers if votes[norm(a)] == top)

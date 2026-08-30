"""Reasoning-path schema definition, parsing, coercion, and display formatting."""

import json
import re

REQUIRED_STEP_KEYS = ("claim", "evidence", "weight")


def blank_path(answer="", confidence=0.0):
    return {
        "answer": str(answer),
        "confidence": float(confidence),
        "steps": [],
        "considered": [],
        "parsed": False,
    }


def _find_json_block(text):
    # Extract markdown code block or parse balanced braces
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        return fence.group(1)
    start = text.find("{")
    while start != -1:
        depth = 0
        in_str = False
        esc = False
        for i in range(start, len(text)):
            c = text[i]
            if esc:
                esc = False
                continue
            if c == "\\":
                esc = True
            elif c == '"' and not esc:
                in_str = not in_str
            elif not in_str:
                if c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        return text[start : i + 1]
        start = text.find("{", start + 1)
    return None


def _as_float(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def _clamp01(x):
    return max(0.0, min(1.0, x))


def _coerce_steps(raw_steps):
    steps = []
    for k, s in enumerate(raw_steps):
        if isinstance(s, str):
            # Handle string steps if dictionary structure was omitted
            steps.append({"id": k + 1, "claim": s.strip(), "evidence": "",
                          "weight": 1.0, "depends_on": []})
            continue
        if not isinstance(s, dict):
            continue
        claim = str(s.get("claim") or s.get("step") or s.get("text") or "").strip()
        if not claim:
            continue
        deps = s.get("depends_on") or []
        if not isinstance(deps, list):
            deps = []
        steps.append({
            "id": int(_as_float(s.get("id"), k + 1)),
            "claim": claim,
            "evidence": str(s.get("evidence") or "").strip(),
            "weight": _as_float(s.get("weight"), 1.0),
            "depends_on": [int(_as_float(d, -1)) for d in deps
                           if _as_float(d, -1) > 0],
        })
    # Normalize weights to sum to 1.0
    total = sum(max(s["weight"], 0.0) for s in steps)
    if total <= 0:
        for s in steps:
            s["weight"] = 1.0 / len(steps) if steps else 0.0
    else:
        for s in steps:
            s["weight"] = max(s["weight"], 0.0) / total
    return steps


def parse_path(text):
    """Model output -> reasoning path dict. Never raises."""
    block = _find_json_block(text or "")
    if block is None:
        return _fallback(text)
    try:
        obj = json.loads(block)
    except json.JSONDecodeError:
        # Clean trailing commas if present
        try:
            obj = json.loads(re.sub(r",\s*([}\]])", r"\1", block))
        except json.JSONDecodeError:
            return _fallback(text)
    if not isinstance(obj, dict):
        return _fallback(text)

    path = blank_path(
        answer=obj.get("answer", ""),
        confidence=_clamp01(_as_float(obj.get("confidence"), 0.5)),
    )
    raw_steps = obj.get("steps")
    if isinstance(raw_steps, list):
        path["steps"] = _coerce_steps(raw_steps)
    considered = obj.get("considered") or obj.get("alternatives") or []
    if isinstance(considered, list):
        path["considered"] = [
            {"answer": str(c.get("answer", "")),
             "reason_rejected": str(c.get("reason_rejected")
                                    or c.get("why_rejected") or "")}
            for c in considered if isinstance(c, dict)
        ]
    path["parsed"] = bool(path["answer"]) and bool(path["steps"])
    if not path["parsed"]:
        return _fallback(text, answer=path["answer"],
                         confidence=path["confidence"])
    return path


def _fallback(text, answer="", confidence=0.3):
    """Fallback representation when output cannot be fully parsed as JSON."""
    text = (text or "").strip()
    if not answer:
        m = re.search(r"(?:final answer|answer)\s*[:=]?\s*(.+)", text,
                      re.IGNORECASE)
        if m:
            answer = m.group(1).strip().splitlines()[0][:80]
    path = blank_path(answer=answer, confidence=confidence)
    if text:
        path["steps"] = [{"id": 1, "claim": text[:600], "evidence": "",
                          "weight": 1.0, "depends_on": []}]
    return path


def parse_loose_json(text):
    """Extract first balanced JSON object from response text."""
    block = _find_json_block(text or "")
    if block is None:
        return None
    try:
        return json.loads(block)
    except json.JSONDecodeError:
        try:
            return json.loads(re.sub(r",\s*([}\]])", r"\1", block))
        except json.JSONDecodeError:
            return None


def path_to_display(path, label):
    """Format reasoning path for peer revision prompt."""
    lines = [f"[{label}] answer: {path['answer']} "
             f"(confidence {path['confidence']:.2f})"]
    for s in path["steps"]:
        dep = f" <- steps {s['depends_on']}" if s["depends_on"] else ""
        ev = f" | evidence: {s['evidence']}" if s["evidence"] else ""
        lines.append(f"  step {s['id']} (w={s['weight']:.2f}){dep}: "
                     f"{s['claim']}{ev}")
    for c in path.get("considered", []):
        if c["answer"]:
            lines.append(f"  considered-and-rejected: {c['answer']}"
                         f" ({c['reason_rejected']})")
    return "\n".join(lines)

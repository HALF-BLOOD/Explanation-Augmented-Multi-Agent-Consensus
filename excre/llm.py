"""Model interfaces and caching layer supporting OpenAI-compatible APIs and deterministic mock models for local testing."""

import hashlib
import json
import os
import random
import re
import time

try:
    import requests
except ImportError:
    requests = None

_last_call = {}   # (base_url, model) -> monotonic time of last request
_hold_until = {}  # (base_url, model) -> when the per-minute token window reopens


class ModelUnavailable(RuntimeError):
    """Raised when a model can't be used for the rest of the session."""

    def __init__(self, model, why):
        super().__init__(f"{model}: {why}")
        self.model = model
        self.why = why


def _seconds(text):
    # groq writes reset times as "1m26.4s" or "637ms"
    units = {"h": 3600, "m": 60, "s": 1, "ms": 0.001}
    return sum(float(n) * units[u]
               for n, u in re.findall(r"([\d.]+)(ms|h|m|s)", text or ""))


def _limit_kind(r):
    m = re.search(r"\((\w+)\): Limit (\d+)", r.text)
    return f" ({m.group(1)} limit {m.group(2)})" if m else ""


def _daily_limit(r):
    # gemini names the quota "...PerDay...", groq says "tokens per day (TPD)"
    if "perday" in r.text.lower().replace(" ", ""):
        return True
    try:
        return float(r.headers.get("retry-after", 0)) > 600
    except ValueError:
        return False


class DiskCache:
    def __init__(self, root):
        self.root = root
        os.makedirs(root, exist_ok=True)

    def _file(self, key):
        h = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return os.path.join(self.root, h[:2], h + ".json")

    def get(self, key):
        f = self._file(key)
        if os.path.exists(f):
            with open(f, encoding="utf-8") as fh:
                return json.load(fh)
        return None

    def put(self, key, value):
        f = self._file(key)
        os.makedirs(os.path.dirname(f), exist_ok=True)
        tmp = f + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(value, fh)
        os.replace(tmp, f)


class OpenAICompatModel:
    def __init__(self, name, base_url, model, api_key_env,
                 min_interval_s=1.0, cache=None, timeout=240,
                 max_tokens_override=None, extra_payload=None,
                 token_floor=0, output_tpm=0, send_seed=True):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key_env = api_key_env
        self.min_interval_s = min_interval_s
        self.cache = cache
        self.timeout = timeout
        # thinking models (gemini 2.5, deepseek v4) burn completion budget on
        # reasoning tokens, so they need a higher cap than the global one
        self.max_tokens_override = max_tokens_override
        self.extra_payload = extra_payload or {}
        self.token_floor = token_floor
        self.output_tpm = output_tpm
        self.send_seed = send_seed

    def _key(self, payload):
        return json.dumps({"u": self.base_url, "p": payload}, sort_keys=True)

    def chat(self, messages, temperature=0.3, max_tokens=900, seed=None):
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": self.max_tokens_override or max_tokens,
        }
        payload.update(self.extra_payload)
        if seed is not None:
            payload["seed"] = seed
        key = self._key(payload)
        if self.cache:
            hit = self.cache.get(key)
            if hit:
                return hit["text"], dict(hit["usage"], cached=True)

        if requests is None:
            raise RuntimeError("pip install requests to use real models")
        api_key = os.environ.get(self.api_key_env, "")
        if not api_key:
            raise ModelUnavailable(self.name, f"{self.api_key_env} is not set")

        gate = (self.base_url, self.model)
        if not self.send_seed:
            # gemini's endpoint rejects the field; the seed still keys the cache
            payload.pop("seed", None)

        # hard ceiling on time spent inside one logical call. nvidia's free
        # endpoint once hung every request for hours; past this point the
        # model is treated as gone for the session and the item stays pending
        deadline = time.monotonic() + 6 * 60
        backoff = 2.0
        wasted = None
        failures = 0
        while failures < 6 and time.monotonic() < deadline:
            now = time.monotonic()
            wait = max(self.min_interval_s - (now - _last_call.get(gate, 0)),
                       _hold_until.get(gate, 0) - now)
            if wait > 0:
                time.sleep(min(wait, 90))
            _last_call[gate] = time.monotonic()
            try:
                r = requests.post(
                    self.base_url + "/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json=payload, timeout=self.timeout,
                )
            except (requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError) as e:
                failures += 1
                print(f"    [{self.name}] {type(e).__name__}, "
                      f"attempt {failures}/6", flush=True)
                time.sleep(backoff + random.uniform(0, 1))
                backoff = min(backoff * 2, 60)
                continue
            if r.status_code == 200:
                body = r.json()
                text = body["choices"][0]["message"]["content"] or ""
                u = body.get("usage") or {}
                spent = u.get("prompt_tokens", 0)
                # gemini leaves thinking tokens out of completion_tokens
                usage = {"prompt_tokens": spent,
                         "completion_tokens": max(u.get("completion_tokens", 0),
                                                  u.get("total_tokens", 0) - spent),
                         "finish": body["choices"][0].get("finish_reason")}
                left = r.headers.get("x-ratelimit-remaining-tokens")
                if left is not None and float(left) < self.token_floor:
                    _hold_until[gate] = time.monotonic() + _seconds(
                        r.headers.get("x-ratelimit-reset-tokens"))
                if self.output_tpm:
                    refill = 60 * usage["completion_tokens"] / self.output_tpm
                    _hold_until[gate] = max(_hold_until.get(gate, 0),
                                            time.monotonic() + refill)
                if not text.strip() and usage["finish"] == "length" and not wasted:
                    # the whole cap went on hidden reasoning: once more with room
                    wasted = usage
                    payload = dict(payload, max_tokens=2 * payload["max_tokens"])
                    continue
                if wasted:
                    usage["prompt_tokens"] += wasted["prompt_tokens"]
                    usage["completion_tokens"] += wasted["completion_tokens"]
                if self.cache:
                    self.cache.put(key, {"text": text, "usage": usage})
                return text, usage
            if r.status_code in (401, 403, 404, 410):
                raise ModelUnavailable(self.name, f"HTTP {r.status_code}: {r.text[:200]}")
            if r.status_code == 429 and _daily_limit(r):
                raise ModelUnavailable(self.name, "daily quota used up")
            if r.status_code in (429, 500, 502, 503):
                retry_after = r.headers.get("retry-after")
                delay = float(retry_after) if retry_after else backoff
                delay = min(delay, 90)
                # per-minute limits are pacing, not failure: only the deadline
                # above ends them, so a busy minute can't bench a model
                if r.status_code == 429:
                    print(f"    [{self.name}] HTTP 429{_limit_kind(r)}, "
                          f"waiting {delay:.0f}s", flush=True)
                else:
                    failures += 1
                    print(f"    [{self.name}] HTTP {r.status_code}, waiting "
                          f"{delay:.0f}s (attempt {failures}/6)", flush=True)
                time.sleep(delay + random.uniform(0, 1))
                backoff = min(backoff * 2, 60)
                continue
            raise RuntimeError(f"{self.name}: HTTP {r.status_code}: {r.text[:300]}")
        raise ModelUnavailable(self.name, "unreachable or rate-limited "
                                          "beyond the retry budget")


class Seeded:
    """One model under another name and seed, for same-model agent groups."""

    def __init__(self, model, seed):
        self.model = model
        self.seed = seed
        self.name = f"{model.name}#{seed}"

    def chat(self, messages, **kw):
        return self.model.chat(messages, **dict(kw, seed=self.seed))


class MockModel:
    """Deterministic mock model for offline testing and pipeline verification."""

    def __init__(self, name, persona=0):
        self.name = name
        self.persona = persona

    def _h(self, *parts):
        s = "|".join(str(p) for p in parts)
        return int(hashlib.md5(s.encode()).hexdigest(), 16)

    def _question(self, prompt):
        m = re.search(r"Problem:\s*(.+?)(?:\n\n|\nOptions:|\Z)", prompt, re.DOTALL)
        return (m.group(1).strip() if m else prompt[:200])

    def _pick_answer(self, prompt, question, seed=None):
        opts = re.findall(r"\(([A-J])\)", prompt)
        if "Yes or No" in prompt:
            pool = ["Yes", "No"]
        elif opts:
            pool = sorted(set(opts))
        else:
            nums = re.findall(r"\d+", question)
            base = sum(int(n) for n in nums[:3]) if nums else 7
            pool = [str(base), str(base), str(base + self.persona % 3)]
        return pool[self._h(question, self.persona, seed, "ans") % len(pool)]

    def chat(self, messages, temperature=0.3, max_tokens=900, seed=None):
        system = " ".join(m["content"] for m in messages if m["role"] == "system")
        prompt = " ".join(m["content"] for m in messages if m["role"] == "user")
        question = self._question(prompt)

        sab = re.search(r'argue for the answer "([^"]+)"', system)
        if sab:
            answer, conf = sab.group(1), 0.9
        else:
            answer = self._pick_answer(prompt, question, seed)
            conf = 0.5 + (self._h(question, self.persona, "c") % 45) / 100.0
            if "Peer reasoning paths:" in prompt or "Peer responses:" in prompt:
                peers = re.findall(r"answer:\s*([^\s(]+)", prompt)
                if peers and self._h(prompt, self.persona) % 4 == 0:
                    answer = peers[0]

        words = [w for w in re.findall(r"[a-zA-Z]{4,}", question)][:6] or ["thing"]

        def step(i):
            w1 = words[self._h(question, answer, i) % len(words)]
            w2 = words[self._h(question, answer, i, "b") % len(words)]
            noise = words[self._h(question, self.persona, i) % len(words)]
            claim = f"Consider {w1} together with {w2}, which points at {answer}."
            if self._h(self.persona, i) % 3 == 0:
                claim += f" Also note {noise}."
            return {"id": i + 1, "claim": claim,
                    "evidence": f"known fact about {w1}",
                    "weight": round(0.2 + (self._h(answer, i) % 60) / 100, 2),
                    "depends_on": [i] if i > 0 else []}

        n_steps = 2 + self._h(question, self.persona, "n") % 3
        usage = {"prompt_tokens": len(prompt) // 4,
                 "completion_tokens": 120 + n_steps * 30}

        if '"steps"' in prompt:
            obj = {"answer": answer, "confidence": round(conf, 2),
                   "steps": [step(i) for i in range(n_steps)],
                   "considered": []}
            return json.dumps(obj), usage
        if '"explanation"' in prompt:
            obj = {"answer": answer, "confidence": round(conf, 2),
                   "explanation": f"Because of {words[0]}, the answer is {answer}."}
            return json.dumps(obj), usage
        lines = [f"Step {i+1}: {step(i)['claim']}" for i in range(n_steps)]
        return "\n".join(lines) + f"\nFinal answer: {answer}", usage


def build_models(model_cfgs, cache_dir=None, use_cache=True):
    cache = DiskCache(cache_dir) if (use_cache and cache_dir) else None
    models = []
    for cfg in model_cfgs:
        kind = cfg.get("kind", "mock")
        if kind == "mock":
            models.append(MockModel(cfg["name"], persona=cfg.get("persona", 0)))
        elif kind == "openai_compat":
            models.append(OpenAICompatModel(
                cfg["name"], cfg["base_url"], cfg["model"],
                cfg["api_key_env"],
                min_interval_s=cfg.get("min_interval_s", 1.0),
                max_tokens_override=cfg.get("max_tokens_override"),
                extra_payload=cfg.get("extra_payload"),
                token_floor=cfg.get("token_floor", 0),
                output_tpm=cfg.get("output_tpm", 0),
                send_seed=cfg.get("send_seed", True),
                cache=cache))
        else:
            raise ValueError(f"unknown model kind: {kind}")
    return models

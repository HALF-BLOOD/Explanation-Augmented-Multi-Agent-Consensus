"""Text similarity backends supporting lexical cosine and Sentence-BERT embeddings."""

import math
import re
from collections import Counter

_STOP = set("""a an and are as at be by for from has have if in is it its of
on or that the this to was were will with which would can could should than
then there their they them we you your not no""".split())

_token_re = re.compile(r"[a-z0-9]+")


def _tokens(text):
    return [t for t in _token_re.findall(text.lower()) if t not in _STOP]


class LexicalSim:
    name = "lexical"

    def sim(self, a, b):
        ta, tb = Counter(_tokens(a)), Counter(_tokens(b))
        if not ta or not tb:
            return 0.0
        dot = sum(ta[t] * tb[t] for t in ta if t in tb)
        na = math.sqrt(sum(v * v for v in ta.values()))
        nb = math.sqrt(sum(v * v for v in tb.values()))
        return dot / (na * nb) if na and nb else 0.0


class SbertSim:
    def __init__(self, model_name="sentence-transformers/all-mpnet-base-v2"):
        import os
        # this box has an old TF/Keras install that transformers trips over;
        # we only ever use the torch path, so keep TF out of it entirely
        os.environ.setdefault("USE_TF", "0")
        os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
        from sentence_transformers import SentenceTransformer  # lazy, heavy
        self.model = SentenceTransformer(model_name)
        self.name = model_name
        self._cache = {}

    def _embed(self, text):
        if text not in self._cache:
            if len(self._cache) > 20000:
                self._cache.clear()
            self._cache[text] = self.model.encode(
                text, normalize_embeddings=True, show_progress_bar=False)
        return self._cache[text]

    def sim(self, a, b):
        if not a.strip() or not b.strip():
            return 0.0
        va, vb = self._embed(a), self._embed(b)
        s = float((va * vb).sum())
        return max(0.0, s)


def build_sim(cfg):
    kind = cfg.get("embedder", "lexical")
    if kind == "lexical":
        return LexicalSim()
    if kind == "sbert":
        return SbertSim(cfg.get("sbert_model",
                                "sentence-transformers/all-mpnet-base-v2"))
    raise ValueError(f"unknown embedder: {kind}")

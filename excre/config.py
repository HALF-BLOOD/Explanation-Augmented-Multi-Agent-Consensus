"""Experiment configuration loader and environment setup."""

import os

import yaml

DEFAULTS = {
    "excre": {"rounds": 3, "devils_advocate": True, "anchor": True,
              "convergence_eps": 0.02, "temperature": 0.3,
              "max_tokens": 900},
    "imrc": {"embedder": "lexical",
             "sbert_model": "sentence-transformers/all-mpnet-base-v2",
             "alpha": 0.5, "beta": 0.2, "gamma": 0.3,
             "evidence_threshold": 0.5},
    "trust": {"w_agreement": 0.35, "w_imrc": 0.35, "w_confidence": 0.20,
              "w_converged": 0.10},
    "sc": {"k": 5, "temperature": 0.7},
    "judge": {"model": None},
    "cache": True,
    "cache_dir": ".cache/llm",
}


def load_config(path):
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    cfg = {}
    for key, default in DEFAULTS.items():
        if isinstance(default, dict):
            cfg[key] = dict(default, **(raw.get(key) or {}))
        else:
            cfg[key] = raw.get(key, default)
    cfg["models"] = raw.get("models") or []
    if not cfg["models"]:
        raise ValueError(f"{path}: no models configured")
    return cfg


def load_dotenv(path=".env"):
    """Load key-value pairs from .env file into os.environ if not already set."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value

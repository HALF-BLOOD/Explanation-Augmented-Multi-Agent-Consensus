# Explanation-Augmented Multi-Agent Consensus (EXCRE)

Code for MSc dissertation (CT7P01NI): Explanation-Augmented Cross-Model Reasoning Exchange. Heterogeneous LLMs solve reasoning problems collaboratively by exchanging structured reasoning paths formatted as schema-validated JSON (atomic steps, evidence references, step weights, and rejected alternatives) over iterative communication rounds. Consensus is scored using Inter-Model Reasoning Congruence (IMRC) -- evaluating whether agents agree on the underlying rationale (*why*), not merely the final prediction (*what*) -- alongside a composite trust score.

Research documentation and theoretical positioning are maintained in [`notes/`](notes/).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Offline Verification (No API Keys Required)

The default configuration uses three deterministic mock models to verify the end-to-end pipeline -- schema parsing, exchange rounds, IMRC computation, trust scoring, checkpointing, and analysis:

```bash
python -m pytest
python run_experiment.py --n 10
python run_experiment.py --n 10 --systems excre --adversarial
python analyze_results.py --results results/dev
```

## Running Experiments

1. Copy `.env.example` to `.env` and set the required API keys.
2. In `configs/default.yaml`, enable target `openai_compat` models and set `imrc.embedder: sbert`.
3. Install full dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Prepare evaluation datasets:
   ```bash
   python prepare_data.py --datasets gsm8k,mmlu,strategyqa,truthfulqa --n 300
   ```
5. Run multi-agent and baseline evaluation:
   ```bash
   python run_experiment.py --data data/gsm8k.jsonl --systems excre,cot,sc,mad,reconcile,judge --out results/gsm8k
   ```

LLM responses are cached locally on disk (`.cache/llm/`) with per-item checkpointing to ensure uninterrupted resumption. Token usage is logged per item for cost and efficiency analysis.

## Repository Structure

```
excre/
  schema.py     Reasoning-path schema: parsing, coercion, repair, and display formatting
  prompts.py    Prompt templates for reasoning exchange rounds and baselines
  llm.py        OpenAI-compatible client, disk cache, rate limiting, and mock models
  embed.py      Text similarity backends (lexical cosine and SBERT)
  imrc.py       Inter-Model Reasoning Congruence (semantic, structural, evidence)
  trust.py      Consensus aggregation, trust components, and fragility metric
  engine.py     Core EXCRE loop: round 0, iterative revision rounds, convergence check
  baselines.py  CoT, Self-Consistency, MAD, ReConcile, and LLM-as-Judge
  data.py       Standardized item format, answer normalization, and benchmark loaders
  runner.py     Per-item checkpointed execution, saboteur rotation, and loop variants
  signals.py    Per-item signals recomputed from stored trails for the analysis
  cara.py       CARA-HYB (Wang & Yang 2026) as a baseline congruence metric
  stats.py      Statistical tests: Wilson CIs, exact McNemar, Spearman, AUROC, risk-coverage, Holm correction
configs/        Experiment configuration files
data/samples/   Validation sample items for offline testing
notes/          Research notes and positioning analysis
tests/          Unit and integration test suites
```

Standalone tools:

```
kaggle_run.py        Staged, resumable runs that commit their results (see below)
paper_report.py      All paper tables from a run folder: accuracy, signal AUROCs,
                     selective prediction, saboteur detection, ablations
rescore.py           Recompute IMRC/trust from stored reasoning trails
                     (embedder and weight variants without new API calls)
make_label_sheet.py  Sample blind path pairs into a CSV for hand-labelling
check_labels.py      Correlate hand labels with IMRC components
```

`configs/main.yaml` is the model set for the paper runs: GPT-OSS 120B and
Qwen3.8 27B via Groq, Gemini 3.5 Flash-Lite via Google. `default.yaml` stays
on offline mocks so tests never need keys.

Systems a run can name: `excre`, `cot:<model>`, `sc:<model>`, `mad`,
`reconcile`, `judge`; the ablations `excre_bare` (no anchor, no devil's
advocate), `excre_noda`, `excre_noanchor` and `excre_same:<model>` (three
seeded copies of one model); and `excre_adv` / `mad_adv` with a rotating
saboteur.

## Running on Kaggle (incremental)

`kaggle_run.py` works through the stages in `configs/kaggle_plan.yaml` in
order. Inside a stage every system gains one block of items per pass, so they
stay on the same questions. A session ends when a provider's free quota or the
session clock runs out; the next one continues from the last commit.

Everything a run produces is committed and pushed every 30 minutes and at the
end of the session:

```
runs/v2/<dataset>/<system>.jsonl     one record per item, with the full trail
runs/v2/data/                        the sampled benchmark items
runs/v2/progress.md                  done/total and accuracy per stage
runs/v2/sessions.jsonl               one line per session
runs/v2/manifest.json                models, settings and prompt hash at the start
runs/cache/                          every model response, keyed by request
```

A run folder is tied to its manifest: if the models, settings or prompts
change later, `kaggle_run.py` stops rather than mix two setups in one folder.
The tables for the paper come from `python paper_report.py --run runs/v2`.

One-time setup:

1. Create a fine-grained GitHub token with *Contents: read and write* on this
   repository only.
2. In a Kaggle notebook, turn Internet on and add these under Add-ons -> Secrets
   (attached to the notebook): `GROQ_API_KEY`, `GEMINI_API_KEY`, `GITHUB_TOKEN`.
3. Put this in a single cell:

```python
import base64, os
from kaggle_secrets import UserSecretsClient

secrets = UserSecretsClient()
for key in ["GROQ_API_KEY", "GEMINI_API_KEY", "GITHUB_TOKEN"]:
    try:
        os.environ[key] = secrets.get_secret(key)
    except Exception:
        print("no secret for", key)

# https auth for git without writing the token into .git/config
auth = base64.b64encode(f"x-access-token:{os.environ['GITHUB_TOKEN']}".encode()).decode()
os.environ.update({"GIT_CONFIG_COUNT": "1",
                   "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
                   "GIT_CONFIG_VALUE_0": f"AUTHORIZATION: basic {auth}"})

!rm -rf /tmp/excre && git clone -q https://github.com/HALF-BLOOD/Explanation-Augmented-Multi-Agent-Consensus.git /tmp/excre
%cd /tmp/excre
!pip install -q -r requirements.txt
!python -u kaggle_run.py --push
```

4. Save Version -> Save & Run All (Commit), so it runs without the browser
   open. Run it again after the quotas reset; it carries on where the last
   session stopped.

When a provider says its daily quota is used up, rejects the key, or stays
unreachable for six minutes, that model is benched, the current block is
finished with the models still up, and the session ends. Groq's free quota is
a daily token allowance per model, so one session a day is all it can feed.
Don't run two sessions at once:
both would append to the same files. The same script runs locally with the
keys from `.env` (leave off `--push` to keep results uncommitted).

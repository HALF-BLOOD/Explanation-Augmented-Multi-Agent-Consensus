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
   pip install -r requirements-full.txt
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
  runner.py     Per-item checkpointed execution and adversarial saboteur rotation
  stats.py      Statistical tests: Wilson CIs, exact McNemar, Spearman, AUROC, risk-coverage, Holm correction
configs/        Experiment configuration files
data/samples/   Validation sample items for offline testing
notes/          Research notes and positioning analysis
tests/          Unit and integration test suites
```

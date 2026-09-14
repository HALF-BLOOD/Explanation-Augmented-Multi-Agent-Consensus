# EXCRE experiment plan (working copy, 14 Sep 2026)

Companion to the positioning note. This is the plan the code is being built
against. Anything here can change once pilot numbers exist; the point is to
have decided the defaults *before* seeing results, so choices aren't made to
flatter the numbers.

## Systems

| id | system | notes |
|---|---|---|
| `cot` | single-model CoT | one call, one model. Report per model and best-of. |
| `sc` | self-consistency, k=5 | the honest single-model baseline (Wang et al. 2023). Matched token budget vs EXCRE matters here. |
| `mad` | free-text multi-agent debate | Du et al. 2023 style, same models and round count as EXCRE. This is the key structured-vs-unstructured control. |
| `reconcile` | ReConcile-style round table | grouped answers + explanations + confidence-weighted vote, adapted from Chen, Saha & Bansal (ACL 2024). No convincing-samples (needs human explanations we don't have for all datasets); document the deviation. |
| `judge` | central judge / Council-Mode-like | independent answers -> one synthesiser model. Approximates Council Mode's shape without their prompts. |
| `excre` | full framework | schema exchange, criss-cross rounds, devil's advocate, IMRC + trust. |

EXCRE ablations (each toggled off separately, on the pilot datasets only):
no-structure (free text but same loop), no-devil's-advocate, no-reasoning-anchor,
single round, trust without IMRC term.

## Models

Requirement: genuinely heterogeneous families, all reachable free or cheap.
Working set (all via OpenAI-compatible endpoints, pinned versions in config):

- Llama 3.3 70B (Groq)
- Qwen 3 32B (Groq or Cerebras)
- Gemini 2.5 Flash (Google AI Studio free tier)
- GPT-OSS 120B or Mistral Small as fourth/swap-in

Groq free tier is 30 req/min, 6k tokens/min, 14.4k req/day per org — workable
for pilots but tight for full runs; the runner therefore needs per-provider
rate limiting, aggressive response caching, and per-item checkpointing so a
run can be killed and resumed without losing paid calls. Budget for the paid
fallback (Groq developer tier + Gemini paid): rough ceiling US$50-100 for the
full grid if caching works; pilot first, then decide.

## Datasets

Phase 1 (pilot + headline): GSM8K (numeric), MMLU (4 mixed subjects, letter),
StrategyQA (yes/no), TruthfulQA mc1 (letter). Covers maths, knowledge,
multi-hop, truthfulness — four different answer formats exercises the whole
pipeline.

Phase 2 (if budget allows): MedQA (high-stakes framing, comparison point with
CARA's domain), BBH subset (convergence stress), LegalBench subset (audit-trail
framing).

n per dataset: 300 test items, fixed random sample, seed written into the
data file. Pilot = 50 items from a *separate* dev slice for prompt/threshold
tuning and the IMRC weight grid. Nothing gets tuned on the 300.

Power reality check: McNemar at n=300 detects roughly 6-8pp differences, so
the accuracy comparisons are reported with CIs and exact p-values but the
paper's primary claims are the correlation/AUROC ones, which are well powered
at n=300 (Spearman rho >= 0.2 detectable, AUROC CIs via bootstrap).

## Metrics and statistics

- Accuracy: Wilson 95% CI; pairwise exact McNemar vs each baseline; Holm
  correction across datasets.
- C1 (IMRC adds signal): logistic regression of correctness on
  {answer-agreement, mean confidence} vs {+ IMRC}; report delta log-likelihood
  and delta AUROC with bootstrap CI. Plus the simple version: Spearman of
  trust vs correctness per system.
- C2 (selective prediction): risk-coverage curves, AURC, accuracy at 70/80/90%
  coverage; gates compared: confidence-only, agreement-only, full trust.
- C3 (saboteur detection): paired clean vs sabotaged runs on the same items;
  AUROC of (agreement - IMRC) gap for flagging sabotaged items; also report
  how often the saboteur flips the consensus answer.
- C4 (structure at matched budget): EXCRE vs `mad` with round count and token
  ceilings matched; report tokens/item and rounds-to-convergence everywhere
  (Smit et al. and Kaesberg et al. both complain nobody reports cost — we do).

## IMRC operational definition (v1, to be validated in the pilot)

Pairwise, three terms, weights alpha/beta/gamma from a small grid search on
pilot data against a hand-labelled congruence set (~60 pairs, labelled by me):

- semantic: one-to-one matching of step claims (Hungarian assignment over
  embedding cosine), normalised by the longer path so unmatched steps cost.
- structural: length ratio + order concordance of matched steps + Jaccard on
  declared dependency edges when present.
- evidence: weight-mass overlap of matched evidence spans (min of normalised
  weights, matched above a cosine threshold).

Embedder: all-mpnet-base-v2 default; report embedder sensitivity (swap
all-MiniLM-L6-v2 and a multilingual one) since the proposal itself flags this
as a limitation. Hand-label agreement (Spearman of IMRC vs my labels) is the
validation number for the metric itself.

Trust score v1: logistic combination of {answer agreement, coalition IMRC,
mean coalition confidence, convergence flag} — weights fitted on GSM8K dev
only, then applied *frozen* to every other dataset. Cross-domain transfer of
the trust weights is itself a reportable result. Also report the fixed
equal-weight version so nobody can say the fit is doing all the work.

## Adversarial insider design

One agent (rotating) receives a hidden instruction: argue for a specified
wrong answer as persuasively as possible, with fabricated-but-plausible
steps, while appearing cooperative. Run on 100 GSM8K + 100 TruthfulQA items,
paired with clean runs. The saboteur's model identity rotates so the effect
isn't confounded with one model's style.

## Order of work

1. Core library: schema, providers with cache/rate-limit/resume, EXCRE engine,
   baselines, IMRC, trust, dataset loaders, stats. Offline mock provider so
   every piece is testable without keys. (This is what's being built now.)
2. Pilot on GSM8K dev slice with real APIs: prompt debugging, schema
   compliance rate (target >95% valid JSON after one repair attempt), token
   cost per item, IMRC weight grid, hand-label session.
3. Freeze config. Phase-1 runs (4 datasets x 6 systems x 300 items).
4. Adversarial runs.
5. Ablations on 2 datasets.
6. Analysis + writing. Phase-2 datasets only if money and time remain.

Decision points: after step 2, if schema compliance <90% on any model, swap
the model, not the schema. After step 3, if C1 fails on all four datasets,
the paper pivots to the failure-taxonomy angle and the thesis reports the
negative result honestly.

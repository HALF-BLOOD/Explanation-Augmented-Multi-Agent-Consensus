# runs/v3

updated 2026-11-25 07:17 UTC, +136 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 35/300 | 35/300 | 35/300 | 34/300 | 34/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 35/300 (97%) | 35/300 (77%) | 35/300 (71%) | 35/300 (97%) | 34/300 (91%) |
| cot:qwen27b | 35/300 (97%) | 35/300 (66%) | 35/300 (69%) | 35/300 (94%) | 34/300 (88%) |
| cot:gemini-flash-lite | 35/300 (97%) | 35/300 (83%) | 35/300 (63%) | 35/300 (100%) | 34/300 (88%) |
| excre | 35/300 (97%) | 35/300 (77%) | 35/300 (80%) | 35/300 (97%) | 34/300 (94%) |
| mad | 35/300 (97%) | 35/300 (83%) | 35/300 (80%) | 34/300 (97%) | 34/300 (91%) |
| sc:gemini-flash-lite | 35/300 (97%) | 35/300 (83%) | 35/300 (63%) | 34/300 (97%) | 34/300 (91%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 35/40 (97%) | 35/40 (77%) |
| mad_adv | 35/40 (97%) | 35/40 (66%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 35/40 (80%) |
| excre_noda | 35/40 (77%) |
| excre_noanchor | 35/40 (74%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 30/30 (67%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 30/30 (80%) | 30/30 (80%) | 30/30 (97%) |
| reconcile | 30/30 (77%) | 30/30 (83%) | 30/30 (97%) |

## schema-order

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| excre_stepsfirst | 35/40 (97%) | 35/40 (80%) | 35/40 (74%) | 34/40 (97%) | 34/40 (94%) |

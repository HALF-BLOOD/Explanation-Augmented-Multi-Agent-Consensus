# runs/v3

updated 2026-11-26 07:03 UTC, +71 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 37/300 | 37/300 | 36/300 | 36/300 | 36/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 37/300 (97%) | 37/300 (76%) | 37/300 (73%) | 36/300 (97%) | 36/300 (89%) |
| cot:qwen27b | 37/300 (97%) | 37/300 (68%) | 37/300 (70%) | 36/300 (94%) | 36/300 (89%) |
| cot:gemini-flash-lite | 37/300 (95%) | 37/300 (78%) | 37/300 (65%) | 36/300 (100%) | 36/300 (89%) |
| excre | 37/300 (95%) | 37/300 (78%) | 37/300 (81%) | 36/300 (97%) | 36/300 (94%) |
| mad | 37/300 (95%) | 37/300 (81%) | 37/300 (81%) | 36/300 (97%) | 36/300 (92%) |
| sc:gemini-flash-lite | 37/300 (95%) | 37/300 (81%) | 37/300 (65%) | 36/300 (97%) | 36/300 (92%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 37/40 (95%) | 37/40 (78%) |
| mad_adv | 37/40 (95%) | 36/40 (67%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 37/40 (81%) |
| excre_noda | 37/40 (78%) |
| excre_noanchor | 37/40 (76%) |

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
| excre_stepsfirst | 37/40 (95%) | 37/40 (78%) | 36/40 (75%) | 36/40 (97%) | 36/40 (94%) |

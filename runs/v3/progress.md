# runs/v3

updated 2026-11-27 06:52 UTC, +76 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 41/300 | 41/300 | 41/300 | 41/300 | 40/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 41/300 (98%) | 41/300 (78%) | 41/300 (76%) | 41/300 (98%) | 41/300 (90%) |
| cot:qwen27b | 41/300 (98%) | 41/300 (71%) | 41/300 (73%) | 41/300 (93%) | 41/300 (88%) |
| cot:gemini-flash-lite | 41/300 (95%) | 41/300 (80%) | 41/300 (68%) | 41/300 (100%) | 41/300 (88%) |
| excre | 41/300 (95%) | 41/300 (78%) | 41/300 (83%) | 41/300 (98%) | 41/300 (95%) |
| mad | 41/300 (95%) | 41/300 (80%) | 41/300 (83%) | 41/300 (98%) | 40/300 (90%) |
| sc:gemini-flash-lite | 41/300 (95%) | 41/300 (83%) | 41/300 (68%) | 41/300 (98%) | 40/300 (90%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 40/40 (95%) | 40/40 (80%) |
| mad_adv | 40/40 (95%) | 40/40 (70%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 40/40 (82%) |
| excre_noda | 40/40 (80%) |
| excre_noanchor | 40/40 (78%) |

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
| excre_stepsfirst | 40/40 (95%) | 40/40 (80%) | 40/40 (78%) | 40/40 (98%) | 40/40 (92%) |

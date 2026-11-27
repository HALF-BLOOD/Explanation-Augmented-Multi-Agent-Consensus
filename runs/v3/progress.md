# runs/v3

updated 2026-11-27 07:23 UTC, +198 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 45/300 | 45/300 | 45/300 | 45/300 | 45/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 45/300 (98%) | 45/300 (78%) | 45/300 (78%) | 45/300 (98%) | 45/300 (89%) |
| cot:qwen27b | 45/300 (98%) | 45/300 (71%) | 45/300 (73%) | 45/300 (93%) | 45/300 (87%) |
| cot:gemini-flash-lite | 45/300 (96%) | 45/300 (82%) | 45/300 (69%) | 45/300 (100%) | 45/300 (87%) |
| excre | 45/300 (96%) | 45/300 (80%) | 45/300 (84%) | 45/300 (98%) | 45/300 (93%) |
| mad | 45/300 (96%) | 45/300 (82%) | 45/300 (84%) | 45/300 (98%) | 45/300 (89%) |
| sc:gemini-flash-lite | 45/300 (96%) | 45/300 (84%) | 45/300 (69%) | 45/300 (98%) | 45/300 (87%) |

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

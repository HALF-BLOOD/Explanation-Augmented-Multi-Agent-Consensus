# runs/v3

updated 2026-11-28 07:57 UTC, +217 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 53/300 | 53/300 | 53/300 | 53/300 | 52/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 53/300 (98%) | 53/300 (79%) | 53/300 (81%) | 53/300 (98%) | 53/300 (85%) |
| cot:qwen27b | 53/300 (98%) | 53/300 (74%) | 53/300 (77%) | 53/300 (94%) | 53/300 (87%) |
| cot:gemini-flash-lite | 53/300 (96%) | 53/300 (81%) | 53/300 (74%) | 53/300 (100%) | 53/300 (81%) |
| excre | 53/300 (96%) | 53/300 (81%) | 53/300 (87%) | 53/300 (98%) | 53/300 (89%) |
| mad | 53/300 (96%) | 53/300 (83%) | 53/300 (87%) | 53/300 (98%) | 53/300 (87%) |
| sc:gemini-flash-lite | 53/300 (96%) | 53/300 (83%) | 53/300 (74%) | 53/300 (98%) | 52/300 (85%) |

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

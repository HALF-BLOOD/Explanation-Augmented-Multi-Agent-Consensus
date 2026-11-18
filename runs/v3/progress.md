# runs/v3

updated 2026-11-18 07:06 UTC, +159 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 15/300 | 14/300 | 14/300 | 14/300 | 14/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 15/300 (93%) | 15/300 (80%) | 14/300 (79%) | 14/300 (100%) | 14/300 (93%) |
| cot:qwen27b | 15/300 (93%) | 15/300 (47%) | 14/300 (71%) | 14/300 (93%) | 14/300 (93%) |
| cot:gemini-flash-lite | 15/300 (93%) | 15/300 (73%) | 14/300 (64%) | 14/300 (100%) | 14/300 (86%) |
| excre | 15/300 (93%) | 15/300 (60%) | 14/300 (71%) | 14/300 (100%) | 14/300 (100%) |
| mad | 15/300 (93%) | 15/300 (80%) | 14/300 (86%) | 14/300 (100%) | 14/300 (93%) |
| sc:gemini-flash-lite | 15/300 (93%) | 14/300 (71%) | 14/300 (64%) | 14/300 (100%) | 14/300 (93%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 15/40 (93%) | 14/40 (79%) |
| mad_adv | 15/40 (93%) | 14/40 (71%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 14/40 (71%) |
| excre_noda | 14/40 (57%) |
| excre_noanchor | 14/40 (57%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 14/30 (43%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 14/30 (64%) | 14/30 (79%) | 14/30 (100%) |
| reconcile | 14/30 (64%) | 14/30 (79%) | 14/30 (100%) |

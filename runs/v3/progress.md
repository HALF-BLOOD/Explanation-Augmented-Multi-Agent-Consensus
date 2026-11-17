# runs/v3

updated 2026-11-17 06:07 UTC, +165 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 10/300 | 10/300 | 9/300 | 9/300 | 9/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 10/300 (90%) | 10/300 (80%) | 10/300 (80%) | 9/300 (100%) | 9/300 (89%) |
| cot:qwen27b | 10/300 (90%) | 10/300 (40%) | 10/300 (70%) | 9/300 (89%) | 9/300 (89%) |
| cot:gemini-flash-lite | 10/300 (90%) | 10/300 (70%) | 10/300 (70%) | 9/300 (100%) | 9/300 (89%) |
| excre | 10/300 (90%) | 10/300 (50%) | 10/300 (60%) | 9/300 (100%) | 9/300 (100%) |
| mad | 10/300 (90%) | 10/300 (80%) | 9/300 (89%) | 9/300 (100%) | 9/300 (89%) |
| sc:gemini-flash-lite | 10/300 (90%) | 10/300 (70%) | 9/300 (67%) | 9/300 (100%) | 9/300 (89%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 10/40 (90%) | 9/40 (67%) |
| mad_adv | 10/40 (90%) | 9/40 (67%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 10/40 (70%) |
| excre_noda | 10/40 (50%) |
| excre_noanchor | 10/40 (50%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 10/30 (30%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 10/30 (60%) | 9/30 (78%) | 9/30 (100%) |
| reconcile | 10/30 (60%) | 9/30 (78%) | 9/30 (100%) |

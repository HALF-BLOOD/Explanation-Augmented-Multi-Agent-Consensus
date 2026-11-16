# runs/v3

updated 2026-11-16 08:40 UTC, +156 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 6/300 | 5/300 | 5/300 | 5/300 | 5/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 6/300 (100%) | 6/300 (100%) | 5/300 (80%) | 5/300 (100%) | 5/300 (80%) |
| cot:qwen27b | 6/300 (100%) | 6/300 (50%) | 5/300 (60%) | 5/300 (80%) | 5/300 (80%) |
| cot:gemini-flash-lite | 6/300 (100%) | 6/300 (67%) | 5/300 (80%) | 5/300 (100%) | 5/300 (100%) |
| excre | 6/300 (100%) | 6/300 (50%) | 5/300 (60%) | 5/300 (100%) | 5/300 (100%) |
| mad | 6/300 (100%) | 6/300 (83%) | 5/300 (80%) | 5/300 (100%) | 5/300 (100%) |
| sc:gemini-flash-lite | 6/300 (100%) | 6/300 (67%) | 5/300 (80%) | 5/300 (100%) | 5/300 (100%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 6/40 (100%) | 5/40 (60%) |
| mad_adv | 6/40 (100%) | 5/40 (60%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 6/40 (67%) |
| excre_noda | 6/40 (50%) |
| excre_noanchor | 6/40 (50%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 6/30 (33%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 5/30 (80%) | 5/30 (80%) | 5/30 (100%) |
| reconcile | 5/30 (60%) | 5/30 (80%) | 5/30 (100%) |

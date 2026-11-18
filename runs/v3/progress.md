# runs/v3

updated 2026-11-18 07:21 UTC, +189 this session, stopped: question 15 waiting on qwen27b  
qwen27b benched: daily quota used up (TPD limit 200000)

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 15/300 | 15/300 | 15/300 | 15/300 | 14/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 15/300 (93%) | 15/300 (80%) | 15/300 (80%) | 15/300 (100%) | 15/300 (93%) |
| cot:qwen27b | 15/300 (93%) | 15/300 (47%) | 15/300 (73%) | 15/300 (93%) | 15/300 (93%) |
| cot:gemini-flash-lite | 15/300 (93%) | 15/300 (73%) | 15/300 (67%) | 15/300 (100%) | 15/300 (87%) |
| excre | 15/300 (93%) | 15/300 (60%) | 15/300 (73%) | 15/300 (100%) | 15/300 (100%) |
| mad | 15/300 (93%) | 15/300 (80%) | 15/300 (87%) | 15/300 (100%) | 14/300 (93%) |
| sc:gemini-flash-lite | 15/300 (93%) | 15/300 (73%) | 15/300 (67%) | 15/300 (100%) | 15/300 (93%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 15/40 (93%) | 15/40 (80%) |
| mad_adv | 15/40 (93%) | 15/40 (73%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 15/40 (73%) |
| excre_noda | 15/40 (60%) |
| excre_noanchor | 15/40 (60%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 15/30 (47%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 15/30 (67%) | 15/30 (80%) | 15/30 (100%) |
| reconcile | 15/30 (67%) | 15/30 (80%) | 15/30 (100%) |

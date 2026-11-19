# runs/v3

updated 2026-11-19 07:46 UTC, +241 this session, stopped: question 21 waiting on qwen27b  
qwen27b benched: daily quota used up (TPD limit 200000)

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 21/300 | 20/300 | 20/300 | 20/300 | 20/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 21/300 (95%) | 21/300 (81%) | 21/300 (76%) | 21/300 (100%) | 21/300 (90%) |
| cot:qwen27b | 21/300 (95%) | 20/300 (60%) | 20/300 (70%) | 20/300 (95%) | 20/300 (85%) |
| cot:gemini-flash-lite | 21/300 (95%) | 21/300 (81%) | 21/300 (67%) | 21/300 (100%) | 21/300 (81%) |
| excre | 21/300 (95%) | 20/300 (65%) | 20/300 (70%) | 20/300 (100%) | 20/300 (90%) |
| mad | 21/300 (95%) | 20/300 (85%) | 20/300 (80%) | 20/300 (100%) | 20/300 (85%) |
| sc:gemini-flash-lite | 21/300 (95%) | 21/300 (81%) | 21/300 (67%) | 21/300 (100%) | 21/300 (86%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 21/40 (95%) | 20/40 (75%) |
| mad_adv | 21/40 (95%) | 20/40 (70%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 20/40 (75%) |
| excre_noda | 20/40 (65%) |
| excre_noanchor | 20/40 (65%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 20/30 (55%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 20/30 (75%) | 20/30 (75%) | 20/30 (100%) |
| reconcile | 20/30 (70%) | 20/30 (75%) | 20/30 (100%) |

# runs/v2

updated 2026-11-15 11:37 UTC, +8 this session, stopped: question 1 waiting on gptoss120b, qwen27b  
gptoss120b benched: daily quota used up (TPD limit 200000)  
qwen27b benched: daily quota used up (TPD limit 200000)

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | medqa | mmlu |
|---|---|---|---|---|
| 1/60 | 0/60 | 0/60 | 0/60 | 0/60 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | medqa | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 10/60 (90%) | 10/60 (80%) | 10/60 (100%) | 0/60 | 0/60 |
| cot:qwen27b | 10/60 (90%) | 10/60 (40%) | 10/60 (80%) | 0/60 | 0/60 |
| cot:gemini-flash-lite | 10/60 (90%) | 10/60 (70%) | 10/60 (80%) | 1/60 (100%) | 1/60 (100%) |
| excre | 10/60 (90%) | 10/60 (50%) | 3/60 (100%) | 0/60 | 0/60 |
| mad | 10/60 (90%) | 10/60 (80%) | 0/60 | 0/60 | 0/60 |
| sc:gemini-flash-lite | 10/60 (90%) | 10/60 (70%) | 10/60 (90%) | 1/60 (100%) | 1/60 (100%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 1/40 (100%) | 0/40 |
| mad_adv | 1/40 (100%) | 0/40 |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 1/40 (100%) |
| excre_noda | 1/40 (0%) |
| excre_noanchor | 0/40 |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 0/30 |

## baselines

| system | strategyqa | truthfulqa | medqa |
|---|---|---|---|
| judge | 0/30 | 0/30 | 0/30 |
| reconcile | 0/30 | 0/30 | 0/30 |

# runs/v3

updated 2026-11-16 07:30 UTC, +1 this session, stopped: question 2 waiting on qwen27b  
qwen27b benched: daily quota used up (TPD limit 200000)

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 2/300 | 2/300 | 2/300 | 1/300 | 1/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 2/300 (100%) | 2/300 (100%) | 2/300 (100%) | 2/300 (100%) | 2/300 (100%) |
| cot:qwen27b | 2/300 (100%) | 2/300 (50%) | 2/300 (50%) | 2/300 (100%) | 1/300 (0%) |
| cot:gemini-flash-lite | 2/300 (100%) | 2/300 (50%) | 2/300 (50%) | 2/300 (100%) | 2/300 (100%) |
| excre | 2/300 (100%) | 2/300 (0%) | 2/300 (50%) | 2/300 (100%) | 1/300 (100%) |
| mad | 2/300 (100%) | 2/300 (100%) | 2/300 (50%) | 1/300 (100%) | 1/300 (100%) |
| sc:gemini-flash-lite | 2/300 (100%) | 2/300 (50%) | 2/300 (100%) | 2/300 (100%) | 2/300 (100%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 2/40 (100%) | 2/40 (50%) |
| mad_adv | 2/40 (100%) | 2/40 (50%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 2/40 (50%) |
| excre_noda | 2/40 (0%) |
| excre_noanchor | 2/40 (0%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 2/30 (0%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 2/30 (100%) | 2/30 (50%) | 1/30 (100%) |
| reconcile | 2/30 (50%) | 2/30 (100%) | 1/30 (100%) |

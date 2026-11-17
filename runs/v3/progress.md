# runs/v3

updated 2026-11-17 06:26 UTC, +215 this session, stopped: question 11 waiting on qwen27b  
qwen27b benched: daily quota used up (TPD limit 200000)

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 11/300 | 11/300 | 10/300 | 10/300 | 10/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 11/300 (91%) | 11/300 (82%) | 11/300 (82%) | 11/300 (100%) | 11/300 (91%) |
| cot:qwen27b | 11/300 (91%) | 11/300 (45%) | 11/300 (73%) | 10/300 (90%) | 10/300 (90%) |
| cot:gemini-flash-lite | 11/300 (91%) | 11/300 (73%) | 11/300 (64%) | 11/300 (100%) | 11/300 (82%) |
| excre | 11/300 (91%) | 11/300 (55%) | 10/300 (60%) | 10/300 (100%) | 10/300 (100%) |
| mad | 11/300 (91%) | 11/300 (82%) | 10/300 (90%) | 10/300 (100%) | 10/300 (90%) |
| sc:gemini-flash-lite | 11/300 (91%) | 11/300 (73%) | 11/300 (64%) | 11/300 (100%) | 11/300 (91%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 11/40 (91%) | 10/40 (70%) |
| mad_adv | 11/40 (91%) | 10/40 (70%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 11/40 (73%) |
| excre_noda | 11/40 (55%) |
| excre_noanchor | 11/40 (55%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 11/30 (36%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 11/30 (64%) | 10/30 (80%) | 10/30 (100%) |
| reconcile | 11/30 (64%) | 10/30 (80%) | 10/30 (100%) |

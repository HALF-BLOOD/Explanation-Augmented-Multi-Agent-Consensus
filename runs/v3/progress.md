# runs/v3

updated 2026-11-20 11:02 UTC, +177 this session, stopped: question 25 waiting on qwen27b  
qwen27b benched: daily quota used up (TPD limit 200000)

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 25/300 | 24/300 | 24/300 | 24/300 | 24/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 25/300 (96%) | 25/300 (80%) | 25/300 (76%) | 25/300 (100%) | 25/300 (92%) |
| cot:qwen27b | 25/300 (96%) | 25/300 (64%) | 24/300 (67%) | 24/300 (96%) | 24/300 (88%) |
| cot:gemini-flash-lite | 25/300 (96%) | 25/300 (84%) | 25/300 (64%) | 25/300 (100%) | 25/300 (84%) |
| excre | 25/300 (96%) | 24/300 (71%) | 24/300 (75%) | 24/300 (100%) | 24/300 (92%) |
| mad | 25/300 (96%) | 24/300 (88%) | 24/300 (83%) | 24/300 (100%) | 24/300 (88%) |
| sc:gemini-flash-lite | 25/300 (96%) | 25/300 (84%) | 25/300 (64%) | 25/300 (100%) | 25/300 (88%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 25/40 (96%) | 24/40 (79%) |
| mad_adv | 25/40 (96%) | 24/40 (67%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 24/40 (79%) |
| excre_noda | 24/40 (71%) |
| excre_noanchor | 24/40 (71%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 24/30 (62%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 24/30 (79%) | 24/30 (75%) | 24/30 (100%) |
| reconcile | 24/30 (75%) | 24/30 (79%) | 24/30 (100%) |

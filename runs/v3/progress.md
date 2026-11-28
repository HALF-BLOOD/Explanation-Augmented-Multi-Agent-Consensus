# runs/v3

updated 2026-11-28 08:10 UTC, +274 this session, stopped: question 55 waiting on gptoss120b  
gptoss120b benched: daily quota used up (TPD limit 200000)

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 55/300 | 55/300 | 55/300 | 54/300 | 54/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 55/300 (98%) | 55/300 (80%) | 55/300 (82%) | 55/300 (98%) | 54/300 (85%) |
| cot:qwen27b | 55/300 (98%) | 55/300 (75%) | 55/300 (78%) | 55/300 (95%) | 55/300 (87%) |
| cot:gemini-flash-lite | 55/300 (95%) | 55/300 (82%) | 55/300 (75%) | 55/300 (100%) | 55/300 (82%) |
| excre | 55/300 (96%) | 55/300 (82%) | 55/300 (87%) | 55/300 (98%) | 54/300 (89%) |
| mad | 55/300 (96%) | 55/300 (84%) | 55/300 (87%) | 54/300 (98%) | 54/300 (87%) |
| sc:gemini-flash-lite | 55/300 (96%) | 55/300 (84%) | 55/300 (75%) | 55/300 (98%) | 55/300 (84%) |

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

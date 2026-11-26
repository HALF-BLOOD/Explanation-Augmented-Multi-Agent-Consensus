# runs/v3

updated 2026-11-26 07:40 UTC, +165 this session, stopped: question 39 waiting on gptoss120b  
gptoss120b benched: daily quota used up (TPD limit 200000)

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 39/300 | 39/300 | 39/300 | 38/300 | 38/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 39/300 (97%) | 39/300 (77%) | 39/300 (74%) | 39/300 (97%) | 38/300 (89%) |
| cot:qwen27b | 39/300 (97%) | 39/300 (69%) | 39/300 (72%) | 39/300 (92%) | 39/300 (90%) |
| cot:gemini-flash-lite | 39/300 (95%) | 39/300 (79%) | 39/300 (67%) | 39/300 (100%) | 39/300 (90%) |
| excre | 39/300 (95%) | 39/300 (79%) | 39/300 (82%) | 39/300 (97%) | 38/300 (95%) |
| mad | 39/300 (95%) | 39/300 (82%) | 39/300 (82%) | 38/300 (97%) | 38/300 (92%) |
| sc:gemini-flash-lite | 39/300 (95%) | 39/300 (82%) | 39/300 (67%) | 39/300 (97%) | 39/300 (92%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 39/40 (95%) | 39/40 (79%) |
| mad_adv | 39/40 (95%) | 39/40 (69%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 39/40 (82%) |
| excre_noda | 39/40 (79%) |
| excre_noanchor | 39/40 (77%) |

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
| excre_stepsfirst | 39/40 (95%) | 39/40 (79%) | 39/40 (77%) | 38/40 (97%) | 38/40 (95%) |

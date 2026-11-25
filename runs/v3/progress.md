# runs/v3

updated 2026-11-25 07:20 UTC, +143 this session, stopped: question 35 waiting on gptoss120b  
gptoss120b benched: daily quota used up (TPD limit 200000)

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 35/300 | 35/300 | 35/300 | 35/300 | 34/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 35/300 (97%) | 35/300 (77%) | 35/300 (71%) | 35/300 (97%) | 35/300 (89%) |
| cot:qwen27b | 35/300 (97%) | 35/300 (66%) | 35/300 (69%) | 35/300 (94%) | 35/300 (89%) |
| cot:gemini-flash-lite | 35/300 (97%) | 35/300 (83%) | 35/300 (63%) | 35/300 (100%) | 35/300 (89%) |
| excre | 35/300 (97%) | 35/300 (77%) | 35/300 (80%) | 35/300 (97%) | 34/300 (94%) |
| mad | 35/300 (97%) | 35/300 (83%) | 35/300 (80%) | 35/300 (97%) | 34/300 (91%) |
| sc:gemini-flash-lite | 35/300 (97%) | 35/300 (83%) | 35/300 (63%) | 35/300 (97%) | 35/300 (91%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 35/40 (97%) | 35/40 (77%) |
| mad_adv | 35/40 (97%) | 35/40 (66%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 35/40 (80%) |
| excre_noda | 35/40 (77%) |
| excre_noanchor | 35/40 (74%) |

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
| excre_stepsfirst | 35/40 (97%) | 35/40 (80%) | 35/40 (74%) | 35/40 (97%) | 34/40 (94%) |

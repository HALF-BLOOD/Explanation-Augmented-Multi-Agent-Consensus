# runs/v3

updated 2026-11-23 07:03 UTC, +75 this session, stopped: question 16 waiting on gptoss120b  
gptoss120b benched: daily quota used up (TPD limit 200000)

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 15/300 | 15/300 | 15/300 | 15/300 | 15/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 32/300 (97%) | 32/300 (75%) | 32/300 (78%) | 32/300 (97%) | 32/300 (91%) |
| cot:qwen27b | 32/300 (97%) | 32/300 (66%) | 32/300 (72%) | 32/300 (94%) | 31/300 (87%) |
| cot:gemini-flash-lite | 32/300 (97%) | 32/300 (88%) | 32/300 (69%) | 32/300 (100%) | 32/300 (88%) |
| excre | 32/300 (97%) | 32/300 (78%) | 32/300 (81%) | 31/300 (97%) | 31/300 (94%) |
| mad | 32/300 (97%) | 32/300 (84%) | 32/300 (84%) | 31/300 (97%) | 31/300 (90%) |
| sc:gemini-flash-lite | 32/300 (97%) | 32/300 (84%) | 32/300 (69%) | 32/300 (97%) | 32/300 (91%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 32/40 (97%) | 32/40 (81%) |
| mad_adv | 32/40 (97%) | 32/40 (72%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 32/40 (81%) |
| excre_noda | 32/40 (78%) |
| excre_noanchor | 32/40 (75%) |

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
| excre_stepsfirst | 15/40 (93%) | 15/40 (73%) | 15/40 (73%) | 15/40 (100%) | 15/40 (100%) |

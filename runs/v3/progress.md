# runs/v3

updated 2026-11-25 06:47 UTC, +59 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 33/300 | 33/300 | 33/300 | 33/300 | 32/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 33/300 (97%) | 33/300 (76%) | 33/300 (76%) | 33/300 (97%) | 33/300 (91%) |
| cot:qwen27b | 33/300 (97%) | 33/300 (64%) | 33/300 (70%) | 33/300 (94%) | 33/300 (88%) |
| cot:gemini-flash-lite | 33/300 (97%) | 33/300 (85%) | 33/300 (67%) | 33/300 (100%) | 33/300 (88%) |
| excre | 33/300 (97%) | 33/300 (76%) | 33/300 (82%) | 33/300 (97%) | 33/300 (94%) |
| mad | 33/300 (97%) | 33/300 (82%) | 33/300 (82%) | 33/300 (97%) | 32/300 (91%) |
| sc:gemini-flash-lite | 33/300 (97%) | 33/300 (82%) | 33/300 (67%) | 33/300 (97%) | 32/300 (91%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 33/40 (97%) | 33/40 (82%) |
| mad_adv | 33/40 (97%) | 33/40 (70%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 33/40 (79%) |
| excre_noda | 33/40 (76%) |
| excre_noanchor | 33/40 (73%) |

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
| excre_stepsfirst | 33/40 (97%) | 33/40 (79%) | 33/40 (76%) | 33/40 (97%) | 32/40 (94%) |

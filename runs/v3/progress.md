# runs/v3

updated 2026-11-28 07:27 UTC, +103 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 49/300 | 49/300 | 49/300 | 49/300 | 49/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 50/300 (98%) | 49/300 (78%) | 49/300 (80%) | 49/300 (98%) | 49/300 (90%) |
| cot:qwen27b | 50/300 (98%) | 49/300 (71%) | 49/300 (76%) | 49/300 (94%) | 49/300 (88%) |
| cot:gemini-flash-lite | 50/300 (96%) | 49/300 (80%) | 49/300 (71%) | 49/300 (100%) | 49/300 (86%) |
| excre | 50/300 (96%) | 49/300 (80%) | 49/300 (86%) | 49/300 (98%) | 49/300 (92%) |
| mad | 50/300 (96%) | 49/300 (82%) | 49/300 (86%) | 49/300 (98%) | 49/300 (90%) |
| sc:gemini-flash-lite | 49/300 (96%) | 49/300 (82%) | 49/300 (71%) | 49/300 (98%) | 49/300 (86%) |

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

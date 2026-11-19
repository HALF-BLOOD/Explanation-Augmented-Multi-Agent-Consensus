# runs/v3

updated 2026-11-19 06:53 UTC, +81 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 17/300 | 17/300 | 17/300 | 16/300 | 16/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 17/300 (94%) | 17/300 (76%) | 17/300 (76%) | 17/300 (100%) | 16/300 (94%) |
| cot:qwen27b | 17/300 (94%) | 17/300 (53%) | 17/300 (71%) | 17/300 (94%) | 16/300 (94%) |
| cot:gemini-flash-lite | 17/300 (94%) | 17/300 (76%) | 17/300 (65%) | 17/300 (100%) | 16/300 (88%) |
| excre | 17/300 (94%) | 17/300 (59%) | 17/300 (71%) | 17/300 (100%) | 16/300 (100%) |
| mad | 17/300 (94%) | 17/300 (82%) | 17/300 (82%) | 17/300 (100%) | 16/300 (94%) |
| sc:gemini-flash-lite | 17/300 (94%) | 17/300 (76%) | 17/300 (65%) | 17/300 (100%) | 16/300 (94%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 17/40 (94%) | 17/40 (76%) |
| mad_adv | 17/40 (94%) | 17/40 (71%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 17/40 (71%) |
| excre_noda | 17/40 (59%) |
| excre_noanchor | 17/40 (59%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 17/30 (47%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 17/30 (71%) | 17/30 (76%) | 16/30 (100%) |
| reconcile | 17/30 (65%) | 17/30 (76%) | 16/30 (100%) |

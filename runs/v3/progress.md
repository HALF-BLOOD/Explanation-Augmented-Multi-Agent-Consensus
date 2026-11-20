# runs/v3

updated 2026-11-20 10:05 UTC, +50 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 22/300 | 22/300 | 21/300 | 21/300 | 21/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 22/300 (95%) | 22/300 (82%) | 22/300 (77%) | 21/300 (100%) | 21/300 (90%) |
| cot:qwen27b | 22/300 (95%) | 22/300 (64%) | 22/300 (68%) | 21/300 (95%) | 21/300 (86%) |
| cot:gemini-flash-lite | 22/300 (95%) | 22/300 (82%) | 22/300 (68%) | 21/300 (100%) | 21/300 (81%) |
| excre | 22/300 (95%) | 22/300 (68%) | 22/300 (73%) | 21/300 (100%) | 21/300 (90%) |
| mad | 22/300 (95%) | 22/300 (86%) | 22/300 (82%) | 21/300 (100%) | 21/300 (86%) |
| sc:gemini-flash-lite | 22/300 (95%) | 22/300 (82%) | 22/300 (68%) | 21/300 (100%) | 21/300 (86%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 22/40 (95%) | 21/40 (76%) |
| mad_adv | 22/40 (95%) | 21/40 (71%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 22/40 (77%) |
| excre_noda | 22/40 (68%) |
| excre_noanchor | 22/40 (68%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 22/30 (59%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 22/30 (77%) | 21/30 (76%) | 21/30 (100%) |
| reconcile | 22/30 (73%) | 21/30 (76%) | 21/30 (100%) |

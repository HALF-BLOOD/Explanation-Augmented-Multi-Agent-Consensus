# runs/v3

updated 2026-11-19 07:23 UTC, +169 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 19/300 | 19/300 | 19/300 | 18/300 | 18/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 19/300 (95%) | 19/300 (79%) | 19/300 (79%) | 19/300 (100%) | 18/300 (94%) |
| cot:qwen27b | 19/300 (95%) | 19/300 (58%) | 19/300 (74%) | 19/300 (95%) | 18/300 (89%) |
| cot:gemini-flash-lite | 19/300 (95%) | 19/300 (79%) | 19/300 (68%) | 19/300 (100%) | 18/300 (83%) |
| excre | 19/300 (95%) | 19/300 (63%) | 19/300 (74%) | 19/300 (100%) | 18/300 (94%) |
| mad | 19/300 (95%) | 19/300 (84%) | 19/300 (84%) | 19/300 (100%) | 18/300 (89%) |
| sc:gemini-flash-lite | 19/300 (95%) | 19/300 (79%) | 19/300 (68%) | 19/300 (100%) | 18/300 (89%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 19/40 (95%) | 19/40 (79%) |
| mad_adv | 19/40 (95%) | 19/40 (74%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 19/40 (74%) |
| excre_noda | 19/40 (63%) |
| excre_noanchor | 19/40 (63%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 19/30 (53%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 19/30 (74%) | 19/30 (79%) | 18/30 (100%) |
| reconcile | 19/30 (68%) | 19/30 (79%) | 18/30 (100%) |

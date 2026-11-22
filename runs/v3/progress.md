# runs/v3

updated 2026-11-22 06:23 UTC, +97 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 31/300 | 31/300 | 31/300 | 31/300 | 31/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 32/300 (97%) | 31/300 (77%) | 31/300 (81%) | 31/300 (97%) | 31/300 (90%) |
| cot:qwen27b | 32/300 (97%) | 31/300 (65%) | 31/300 (74%) | 31/300 (94%) | 31/300 (87%) |
| cot:gemini-flash-lite | 32/300 (97%) | 31/300 (87%) | 31/300 (71%) | 31/300 (100%) | 31/300 (87%) |
| excre | 32/300 (97%) | 31/300 (77%) | 31/300 (81%) | 31/300 (97%) | 31/300 (94%) |
| mad | 32/300 (97%) | 31/300 (84%) | 31/300 (87%) | 31/300 (97%) | 31/300 (90%) |
| sc:gemini-flash-lite | 31/300 (97%) | 31/300 (84%) | 31/300 (71%) | 31/300 (97%) | 31/300 (90%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 31/40 (97%) | 31/40 (84%) |
| mad_adv | 31/40 (97%) | 31/40 (74%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 31/40 (81%) |
| excre_noda | 31/40 (77%) |
| excre_noanchor | 31/40 (74%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 30/30 (67%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 30/30 (80%) | 30/30 (80%) | 30/30 (97%) |
| reconcile | 30/30 (77%) | 30/30 (83%) | 30/30 (97%) |

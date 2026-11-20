# runs/v3

updated 2026-11-20 10:35 UTC, +119 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 23/300 | 23/300 | 23/300 | 23/300 | 23/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 24/300 (96%) | 23/300 (78%) | 23/300 (74%) | 23/300 (100%) | 23/300 (91%) |
| cot:qwen27b | 24/300 (96%) | 23/300 (61%) | 23/300 (65%) | 23/300 (96%) | 23/300 (87%) |
| cot:gemini-flash-lite | 24/300 (96%) | 23/300 (83%) | 23/300 (65%) | 23/300 (100%) | 23/300 (83%) |
| excre | 24/300 (96%) | 23/300 (70%) | 23/300 (74%) | 23/300 (100%) | 23/300 (91%) |
| mad | 24/300 (96%) | 23/300 (87%) | 23/300 (83%) | 23/300 (100%) | 23/300 (87%) |
| sc:gemini-flash-lite | 24/300 (96%) | 23/300 (83%) | 23/300 (65%) | 23/300 (100%) | 23/300 (87%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 24/40 (96%) | 23/40 (78%) |
| mad_adv | 23/40 (96%) | 23/40 (70%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 23/40 (78%) |
| excre_noda | 23/40 (70%) |
| excre_noanchor | 23/40 (70%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 23/30 (61%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 23/30 (78%) | 23/30 (74%) | 23/30 (100%) |
| reconcile | 23/30 (74%) | 23/30 (78%) | 23/30 (100%) |

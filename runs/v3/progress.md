# runs/v3

updated 2026-11-21 15:51 UTC, +84 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 27/300 | 26/300 | 26/300 | 26/300 | 26/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 27/300 (96%) | 27/300 (81%) | 26/300 (77%) | 26/300 (100%) | 26/300 (92%) |
| cot:qwen27b | 27/300 (96%) | 27/300 (67%) | 26/300 (69%) | 26/300 (96%) | 26/300 (88%) |
| cot:gemini-flash-lite | 27/300 (96%) | 27/300 (85%) | 26/300 (65%) | 26/300 (100%) | 26/300 (85%) |
| excre | 27/300 (96%) | 27/300 (74%) | 26/300 (77%) | 26/300 (100%) | 26/300 (92%) |
| mad | 27/300 (96%) | 27/300 (89%) | 26/300 (85%) | 26/300 (100%) | 26/300 (88%) |
| sc:gemini-flash-lite | 27/300 (96%) | 27/300 (85%) | 26/300 (65%) | 26/300 (100%) | 26/300 (88%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 27/40 (96%) | 26/40 (81%) |
| mad_adv | 27/40 (96%) | 26/40 (69%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 27/40 (81%) |
| excre_noda | 27/40 (74%) |
| excre_noanchor | 27/40 (74%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 26/30 (65%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 26/30 (81%) | 26/30 (77%) | 26/30 (100%) |
| reconcile | 26/30 (77%) | 26/30 (81%) | 26/30 (100%) |

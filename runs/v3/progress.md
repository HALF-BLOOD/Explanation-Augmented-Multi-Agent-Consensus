# runs/v3

updated 2026-11-21 16:23 UTC, +163 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 29/300 | 28/300 | 28/300 | 28/300 | 28/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 29/300 (97%) | 28/300 (82%) | 28/300 (79%) | 28/300 (96%) | 28/300 (93%) |
| cot:qwen27b | 29/300 (97%) | 28/300 (64%) | 28/300 (71%) | 28/300 (93%) | 28/300 (89%) |
| cot:gemini-flash-lite | 29/300 (97%) | 28/300 (86%) | 28/300 (68%) | 28/300 (100%) | 28/300 (86%) |
| excre | 29/300 (97%) | 28/300 (75%) | 28/300 (79%) | 28/300 (96%) | 28/300 (93%) |
| mad | 29/300 (97%) | 28/300 (89%) | 28/300 (86%) | 28/300 (96%) | 28/300 (89%) |
| sc:gemini-flash-lite | 29/300 (97%) | 28/300 (86%) | 28/300 (68%) | 28/300 (96%) | 28/300 (89%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 29/40 (97%) | 28/40 (82%) |
| mad_adv | 29/40 (97%) | 28/40 (71%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 28/40 (79%) |
| excre_noda | 28/40 (75%) |
| excre_noanchor | 28/40 (71%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 28/30 (64%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 28/30 (82%) | 28/30 (79%) | 28/30 (96%) |
| reconcile | 28/30 (79%) | 28/30 (82%) | 28/30 (96%) |

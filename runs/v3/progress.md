# runs/v3

updated 2026-11-17 05:37 UTC, +84 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 8/300 | 8/300 | 8/300 | 7/300 | 7/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 8/300 (100%) | 8/300 (88%) | 8/300 (88%) | 8/300 (100%) | 7/300 (86%) |
| cot:qwen27b | 8/300 (100%) | 8/300 (50%) | 8/300 (62%) | 7/300 (86%) | 7/300 (86%) |
| cot:gemini-flash-lite | 8/300 (100%) | 8/300 (75%) | 8/300 (62%) | 7/300 (100%) | 7/300 (86%) |
| excre | 8/300 (100%) | 8/300 (50%) | 8/300 (50%) | 7/300 (100%) | 7/300 (100%) |
| mad | 8/300 (100%) | 8/300 (88%) | 8/300 (88%) | 7/300 (100%) | 7/300 (86%) |
| sc:gemini-flash-lite | 8/300 (100%) | 8/300 (75%) | 8/300 (62%) | 7/300 (100%) | 7/300 (86%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 8/40 (100%) | 8/40 (62%) |
| mad_adv | 8/40 (100%) | 8/40 (75%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 8/40 (62%) |
| excre_noda | 8/40 (50%) |
| excre_noanchor | 8/40 (50%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 8/30 (38%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 8/30 (75%) | 8/30 (75%) | 7/30 (100%) |
| reconcile | 8/30 (62%) | 8/30 (75%) | 7/30 (100%) |

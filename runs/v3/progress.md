# runs/v3

updated 2026-11-16 08:08 UTC, +77 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 4/300 | 4/300 | 3/300 | 3/300 | 3/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 4/300 (100%) | 4/300 (100%) | 4/300 (75%) | 3/300 (100%) | 3/300 (100%) |
| cot:qwen27b | 4/300 (100%) | 4/300 (50%) | 4/300 (50%) | 3/300 (100%) | 3/300 (67%) |
| cot:gemini-flash-lite | 4/300 (100%) | 4/300 (50%) | 4/300 (75%) | 3/300 (100%) | 3/300 (100%) |
| excre | 4/300 (100%) | 4/300 (25%) | 4/300 (50%) | 3/300 (100%) | 3/300 (100%) |
| mad | 4/300 (100%) | 4/300 (75%) | 4/300 (75%) | 3/300 (100%) | 3/300 (100%) |
| sc:gemini-flash-lite | 4/300 (100%) | 4/300 (50%) | 4/300 (75%) | 3/300 (100%) | 3/300 (100%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 4/40 (100%) | 4/40 (50%) |
| mad_adv | 4/40 (100%) | 3/40 (67%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 4/40 (50%) |
| excre_noda | 4/40 (25%) |
| excre_noanchor | 4/40 (25%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 4/30 (25%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 4/30 (75%) | 3/30 (67%) | 3/30 (100%) |
| reconcile | 4/30 (50%) | 3/30 (100%) | 3/30 (100%) |

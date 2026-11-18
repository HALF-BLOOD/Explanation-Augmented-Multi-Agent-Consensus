# runs/v3

updated 2026-11-18 06:35 UTC, +66 this session

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 13/300 | 12/300 | 12/300 | 12/300 | 12/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 13/300 (92%) | 12/300 (83%) | 12/300 (75%) | 12/300 (100%) | 12/300 (92%) |
| cot:qwen27b | 13/300 (92%) | 12/300 (50%) | 12/300 (67%) | 12/300 (92%) | 12/300 (92%) |
| cot:gemini-flash-lite | 13/300 (92%) | 12/300 (75%) | 12/300 (58%) | 12/300 (100%) | 12/300 (83%) |
| excre | 13/300 (92%) | 12/300 (58%) | 12/300 (67%) | 12/300 (100%) | 12/300 (100%) |
| mad | 13/300 (92%) | 12/300 (83%) | 12/300 (83%) | 12/300 (100%) | 12/300 (92%) |
| sc:gemini-flash-lite | 13/300 (92%) | 12/300 (75%) | 12/300 (58%) | 12/300 (100%) | 12/300 (92%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 13/40 (92%) | 12/40 (75%) |
| mad_adv | 13/40 (92%) | 12/40 (67%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 12/40 (75%) |
| excre_noda | 12/40 (58%) |
| excre_noanchor | 12/40 (58%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 12/30 (42%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 12/30 (67%) | 12/30 (75%) | 12/30 (100%) |
| reconcile | 12/30 (67%) | 12/30 (75%) | 12/30 (100%) |

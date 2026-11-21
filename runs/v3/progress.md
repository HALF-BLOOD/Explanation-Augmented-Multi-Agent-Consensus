# runs/v3

updated 2026-11-21 16:39 UTC, +188 this session, stopped: question 29 waiting on qwen27b  
qwen27b benched: daily quota used up (TPD limit 200000)

questions finished by every system that runs them

| gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|
| 29/300 | 29/300 | 28/300 | 28/300 | 28/300 |

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa | arc_challenge | mmlu |
|---|---|---|---|---|---|
| cot:gptoss120b | 29/300 (97%) | 29/300 (79%) | 29/300 (79%) | 29/300 (97%) | 29/300 (90%) |
| cot:qwen27b | 29/300 (97%) | 29/300 (66%) | 29/300 (72%) | 28/300 (93%) | 28/300 (89%) |
| cot:gemini-flash-lite | 29/300 (97%) | 29/300 (86%) | 29/300 (69%) | 29/300 (100%) | 29/300 (86%) |
| excre | 29/300 (97%) | 29/300 (76%) | 29/300 (79%) | 28/300 (96%) | 28/300 (93%) |
| mad | 29/300 (97%) | 29/300 (86%) | 29/300 (86%) | 28/300 (96%) | 28/300 (89%) |
| sc:gemini-flash-lite | 29/300 (97%) | 29/300 (86%) | 29/300 (69%) | 29/300 (97%) | 29/300 (90%) |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 29/40 (97%) | 29/40 (83%) |
| mad_adv | 29/40 (97%) | 28/40 (71%) |

## ablations

| system | strategyqa |
|---|---|
| excre_bare | 29/40 (79%) |
| excre_noda | 29/40 (76%) |
| excre_noanchor | 29/40 (72%) |

## same-model

| system | strategyqa |
|---|---|
| excre_same:qwen27b | 29/30 (66%) |

## baselines

| system | strategyqa | truthfulqa | arc_challenge |
|---|---|---|---|
| judge | 29/30 (79%) | 28/30 (79%) | 28/30 (96%) |
| reconcile | 29/30 (76%) | 28/30 (82%) | 28/30 (96%) |

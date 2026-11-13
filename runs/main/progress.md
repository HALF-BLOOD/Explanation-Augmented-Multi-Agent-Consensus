# runs/main

updated 2026-11-13 07:24 UTC, +48 this session

done / total (accuracy so far)

## core

| system | gsm8k | strategyqa | truthfulqa |
|---|---|---|---|
| cot:gptoss120b | 10/100 (90%) | 0/100 | 0/100 |
| cot:qwen27b | 10/100 (90%) | 0/100 | 0/100 |
| cot:gemini-flash-lite | 10/100 (90%) | 0/100 | 0/100 |
| excre | 10/100 (90%) | 0/100 | 0/100 |
| mad | 8/100 (100%) | 0/100 | 0/100 |
| sc:gemini-flash-lite | 0/100 | 0/100 | 0/100 |

## saboteur

| system | gsm8k | truthfulqa |
|---|---|---|
| excre_adv | 0/50 | 0/50 |
| mad_adv | 0/50 | 0/50 |

## ablations

| system | gsm8k | strategyqa |
|---|---|---|
| excre_bare | 0/50 | 0/50 |
| excre_noda | 0/50 | 0/50 |
| excre_noanchor | 0/50 | 0/50 |

## same-model

| system | gsm8k | strategyqa |
|---|---|---|
| excre_same:qwen27b | 0/50 | 0/50 |

## more-baselines

| system | gsm8k | strategyqa | truthfulqa |
|---|---|---|---|
| judge | 0/100 | 0/100 | 0/100 |
| reconcile | 0/100 | 0/100 | 0/100 |
| sc:gptoss120b | 0/100 | 0/100 | 0/100 |
| sc:qwen27b | 0/100 | 0/100 | 0/100 |

## medqa

| system | medqa |
|---|---|
| cot:gptoss120b | 0/100 |
| cot:qwen27b | 0/100 |
| cot:gemini-flash-lite | 0/100 |
| excre | 0/100 |
| mad | 0/100 |

## extend

| system | gsm8k | strategyqa | truthfulqa | mmlu |
|---|---|---|---|---|
| cot:gptoss120b | 10/300 (90%) | 0/300 | 0/300 | 0/300 |
| cot:qwen27b | 10/300 (90%) | 0/300 | 0/300 | 0/300 |
| cot:gemini-flash-lite | 10/300 (90%) | 0/300 | 0/300 | 0/300 |
| excre | 10/300 (90%) | 0/300 | 0/300 | 0/300 |
| mad | 8/300 (100%) | 0/300 | 0/300 | 0/300 |
| sc:gemini-flash-lite | 0/300 | 0/300 | 0/300 | 0/300 |

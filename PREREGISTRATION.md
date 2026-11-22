# Pre-registration: reasoning congruence before and after the exchange

Written 22 Nov 2026 and committed before any of the confirmation data below was collected; the commit date is the timestamp. The analysis code is section 2b of `paper_report.py`, committed alongside it.

## What had been seen

Questions 1–32 of every dataset in `runs/v3` (158 EXCRE items, 17 wrong) were analysed before this was written.

The original claim C1 was that final coalition IMRC predicts a correct answer beyond answer agreement. It was not supported: AUROC 0.33 [0.20, 0.47]. Coalition IMRC before the exchange pointed the other way (0.65), and so did the rise in IMRC during the exchange (AUROC of −induced 0.81). The hypotheses below come from that data, so questions 1–32 are not used to confirm them.

## Hypotheses

- **H1.** Coalition IMRC at round 0, before the agents see each other, predicts a correct final answer: AUROC > 0.5.
- **H2.** The rise in coalition IMRC during the exchange flags wrong answers: AUROC of −induced > 0.5, where induced = final coalition IMRC − round-0 coalition IMRC over the same agents.
- **H3.** Final coalition IMRC does not predict a correct answer: its AUROC is not above 0.5.
- **H4.** Round-0 IMRC and induced together add to answer agreement plus mean confidence: out-of-fold AUROC gain > 0.
- **R.** H1–H3 hold when the schema asks for the steps before the answer (`excre_stepsfirst`).

## Data

- **Confirmation set:** `excre` records for questions 33–300 of every dataset (item ids `-0032` onward). None of these existed when this was written.
- **Robustness set:** every `excre_stepsfirst` record, i.e. questions 1–40 of every dataset, all run after this commit.
- **No exclusions.** Replies cut off at a token cap and replies the parser could not read stay in as recorded.
- Models, prompts and settings stay frozen by `runs/v3/manifest.json`.

## Tests

- AUROC is pooled over the five datasets, with a 95% percentile bootstrap interval (`python paper_report.py --run runs/v3 --boot 2000`).
- **H1 and H2** are supported when the interval lies above 0.5.
- **H3** is supported when the interval does not lie above 0.5.
- **H4** is tested with 5-fold out-of-fold logistic regression (agreement + confidence, with and without round-0 IMRC + induced). It is supported when the bootstrap interval of the gain lies above 0.
- **R** is read with the same rules on the robustness set.
- Per-dataset results are reported as secondary.

## Exploratory

Everything else is reported as exploratory: results on questions 1–32, the other signals, per-dataset breakdowns, the ablations, and any analysis not listed here.

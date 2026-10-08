# CELL-058 — Hierarchical FadeMem Cache Probe

Priority: P0

Status: candidate-with-runnable-probe

Source IDs: SRC-0120

## Cheap first run

Coarse/mid/fine stream with old anchors and dense-near/sparse-far interval summaries.

## Baselines

- sliding window
- first plus recent
- uniform blocks
- FadeMem power bins
- FadeMem anchor power
- oracle anchors

## Metrics

- cosine
- MSE
- covered mass
- weighted interval width
- anchor recall

## Stop condition

If hierarchy loses to first+recent on mixed/anchor regimes, reject fixed power schedule.

# CELL-057 — ART Runtime Termination Probe

Priority: P1

Status: candidate-with-runnable-probe

Source IDs: SRC-0109

## Cheap first run

Blockwise attention traversal with output-stability stopping.

## Baselines

- sequential blocks
- recency-first blocks
- attention-mass-desc blocks
- full attention

## Metrics

- read fraction
- cosine to full
- MSE to full
- stop rate

## Stop condition

If late surprises defeat all cheap criteria, require oracle/order model before more work.

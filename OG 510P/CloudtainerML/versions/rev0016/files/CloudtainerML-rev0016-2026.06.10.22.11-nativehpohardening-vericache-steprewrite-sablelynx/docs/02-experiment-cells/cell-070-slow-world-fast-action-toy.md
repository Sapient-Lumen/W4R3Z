# CELL-070 — Slow-World / Fast-Action Toy

Priority: **P2**
Status: `candidate`

## Cheapest first run

Two-timescale hidden-state stream: slow global state, fast local action decisions, stale observations.

## Baselines

- synchronous update
- slow memory
- query-routed memory
- oracle state

## Metrics

- action accuracy
- state error
- memory update count
- staleness failures

## Stop condition

If slow memory cannot beat synchronous under any update budget, keep as analogy.

## Source ids

SRC-0124, SRC-0120

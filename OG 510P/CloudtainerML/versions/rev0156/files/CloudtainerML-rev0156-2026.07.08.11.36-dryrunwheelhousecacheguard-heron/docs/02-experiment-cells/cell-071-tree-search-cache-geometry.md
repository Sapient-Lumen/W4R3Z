# CELL-071 — Tree-Search Cache Geometry

Priority: **P1**
Status: `candidate`

## Cheapest first run

Branching path simulator with backtracking; compare flat cache policies to ancestor-aware and branch-value policies.

## Baselines

- full tree retention
- LRU
- active path only
- ancestor-aware
- value-estimator policy

## Metrics

- peak cache
- rehydration count
- winner preserved
- branch latency
- accuracy

## Stop condition

If tree-aware policy reduces to LRU under varied branch distributions, deprioritize.

## Source ids

SRC-0125, SRC-0126

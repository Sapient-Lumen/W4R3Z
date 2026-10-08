# CELL-217 — Bankwise Sparse Gating Probe

Priority: **P1**  
Status: **runnable**  
Idea: `IDEA-0216`  
Sources: SRC-0243

## Cheap first run

Run experiments/bankwise_sparse_gating/bankwise_sparse_probe.cpp.

## Metrics

- important channel recall
- FLOP fraction
- miss rate
- repair trigger
- utility

## Required baselines

- dense
- global top-k
- bankwise top-k
- random bankwise
- single-layer repair
- oracle bankwise

## Stop condition

If global top-k wins all non-oracle regimes, keep as P2.

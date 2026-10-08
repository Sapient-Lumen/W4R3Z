# CELL-301 — Incremental Sparse-Attention Markov Lag Task

Priority: **P1**  
Status: `future-trained-candidate`

## Cheap first run
Train tiny transformer on high-order Markov chain with known lag importances; inspect staged attention acquisition.

## Metrics
- lag acquisition step
- validation loss
- attention support
- seed stability

## Required baselines
- full attention
- local attention
- sparse attention
- linear model

## Stop condition
Demote if stages are not seed-stable.

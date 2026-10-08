# CELL-291 — Sparse/Low-Rank Hybrid Frontier

Priority: **P0**  
Status: **runnable-native**

## Why this cell exists
Run sparse_lowrank_hybrid_frontier.cpp to compare dense, sparse, low-rank, hybrid, and entropy-switch policies.

## Question
Linked idea: `IDEA-0289`.

## Sources
- `SRC-0274`
- `SRC-0314`

## Metrics
- approx_error
- tail_error
- wall_proxy
- score

## Required baselines
- dense full
- sparse top-k
- low-rank kernel
- oracle frontier

## Stop condition
Demote hybrid if it does not beat simpler sparse/lowrank baselines under wall and tail penalties.

## Rev0027 note
Performance-first lane. Security/trust side-wing material is not driving this cell.

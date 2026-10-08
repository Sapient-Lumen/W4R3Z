# CELL-291 — Sparse/Low-Rank Hybrid Frontier

Priority: **P0**  
Status: **runnable-native**

## Cheap first run
Run sparse_lowrank_hybrid_frontier.cpp to compare dense, sparse, low-rank, hybrid, and entropy-switch policies.

## Linked idea
`IDEA-0289`

## Sources
- `SRC-0274`
- `SRC-0314`

## Metrics
- approx_error
- tail_error
- wall_proxy
- score

## Stop condition
Demote hybrid if it does not beat simpler sparse/lowrank baselines under wall and tail penalties.

## Rev0027 note
Performance-first cell; security/trust side-wing is not driving this priority.

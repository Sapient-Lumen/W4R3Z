# CELL-266 — Sigma-Branch Single-Path Dynamic Inference

Priority: **P1**  
Status: `future-native`  
Sources: SRC-0285

## Question

Does hierarchical single-path execution beat flat sparse routing under equal active-parameter budgets?

## Cheap first run

Extend tree-sparse FFN with shared trunk / branch-specialist / leaf-specialist cost model.

## Metrics

- `active_params`
- `route_error`
- `rare_path_recall`
- `score`

## Required baselines

- `dense`
- `flat_topk_router`
- `tree_auto_prune`

## Stop condition

Promote if single-path trees win equal active-parameter budgets without rare-path failure.

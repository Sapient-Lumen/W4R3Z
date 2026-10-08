# CELL-355 — Hybrid Sparse Mask Compiler Frontier

Priority: **P1**  
Status: queued

## Question

Do hybrid Top-k/Top-p/threshold compilers beat single-rule sparse mask compilation under uniform, skewed, and false-spike attention rows?

## Cheap first run

Extend gate_compiler_frontier.cpp with Top-p and hybrid Top-k+Top-p compilers plus compensated threshold baselines.

## Metrics

- `score`
- `reachable`
- `miss`
- `selected`
- `calibration_error`
- `rank_quality`
- `regret`
- `cost`

## Required baselines

- `threshold_0p5`
- `topk_budget3`
- `top_p_mass`
- `hybrid_topk_topp`
- `validation_topk_budget`

## Stop condition

Promote only if hybrid masks beat simple top-k/threshold under held-out row shapes and selector-cost guards.

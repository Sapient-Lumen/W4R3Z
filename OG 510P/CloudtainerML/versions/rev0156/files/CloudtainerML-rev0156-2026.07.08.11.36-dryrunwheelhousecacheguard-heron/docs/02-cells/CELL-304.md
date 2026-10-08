# CELL-304 — Meta-Attention Mechanism Router Toy

Priority: **P1**  
Status: `runnable-native`

## Why this exists
experiments/meta_attention_router/meta_attention_router.cpp compares always-full/local/linear/spectral with deterministic, cost-prior, Bayesian, and hard-posterior routers.

## Metrics
- quality
- cost_frac
- budget_over
- route_miss
- uncertainty_error
- collapse_penalty
- posterior_entropy
- score

## Required baselines
- always_full
- always_local
- always_linear
- always_spectral
- oracle_mechanism

## Stop condition
If posterior uncertainty never beats deterministic routing outside oracle cases, keep as P1.

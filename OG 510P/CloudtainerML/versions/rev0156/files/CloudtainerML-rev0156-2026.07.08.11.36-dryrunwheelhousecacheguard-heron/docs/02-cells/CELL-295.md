# CELL-295 — Spectral Operator Routing Wind Tunnel

Priority: **P0**  
Status: `native-probe-added`

## Why this exists
experiments/spectral_operator_routing/spectral_operator_routing.cpp compares full attention, DCT-only, RBF-only, DCT+attention, entropy routing, and oracle mix under equal budget.

## Metrics
- score
- error
- flops
- budget_over
- route_miss
- alias_error
- regret

## Required baselines
- full_attention
- dct_only
- collapse_dct_attention
- spectral_entropy_router
- oracle_operator_mix

## Stop condition
Promote only if wins survive alias/high-frequency traps and equal-cost budgets.

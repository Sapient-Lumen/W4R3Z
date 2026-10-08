# CELL-306 — Null Expert Data Sparsity and Rare Guard

Priority: **P1**  
Status: `runnable-native`

## Why this exists
experiments/null_expert_data_sparsity/null_expert_data_sparsity.cpp tests null experts, rare guards, aggressive skip, and balanced routers.

## Metrics
- quality
- active_compute
- budget_over
- false_skip
- load_imbalance
- rare_miss
- regret
- score

## Required baselines
- dense_ffn
- token_choice_top2
- token_choice_with_null
- aggressive_null
- oracle_null_policy

## Stop condition
If rare-miss destroys the compute win across regimes, only use null experts as low-information-token filter.

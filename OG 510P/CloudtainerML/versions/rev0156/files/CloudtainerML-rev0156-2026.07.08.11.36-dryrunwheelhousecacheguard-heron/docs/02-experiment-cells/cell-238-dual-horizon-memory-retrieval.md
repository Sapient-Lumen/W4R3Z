# CELL-238 — Dual-Horizon Memory Retrieval

Priority: **P1**  
Status: **implemented-native-rev0020**  
Idea: `IDEA-0237`  
Sources: SRC-0263

## Cheap first run

Run experiments/horizon_memory_retrieval/horizon_memory_retrieval_probe.cpp; compare global and local memory allocation.

## Metrics

- mean_global_strategy_score
- mean_local_debug_score
- mean_turns
- mean_success
- mean_utility

## Required baselines

- no_memory
- static_similarity
- episode_only
- turn_only
- dual_horizon_static
- dual_horizon_prm_toy
- oracle_horizon

## Stop condition

If single-horizon policies dominate, reserve dual-horizon for later trained environments.

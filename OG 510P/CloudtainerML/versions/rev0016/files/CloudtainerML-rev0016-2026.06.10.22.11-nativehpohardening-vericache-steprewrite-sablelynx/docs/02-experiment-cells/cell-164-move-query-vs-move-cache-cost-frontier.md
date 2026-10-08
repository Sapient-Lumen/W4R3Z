# CELL-164 — Move Query vs Move Cache Cost Frontier

Priority: **P0**  
Status: **runnable-native-probe**  
Idea: `IDEA-0163` — Move-query-vs-move-cache cost predicate

## Core question

For sparse/latent attention, when should a system ship query rows instead of fetching KV chunks?

## Source anchors

- `SRC-0202` — Move the Query, Not the Cache: Characterizing Cross-Instance Latent and Sparse Attention Redistribution Across GPU Fabrics (https://arxiv.org/abs/2606.01502)

## Cheap first run

experiments/query_move_cache/query_move_probe.cpp emits REV0013_QUERY_MOVE_CACHE_SMOKE.json.

## Metrics

- estimated_us
- winner_counts
- fabric sensitivity
- payload crossover

## Required baselines

- move cache
- move query
- local recompute

## Falsifier / stop condition

If no nontrivial phase boundary appears, keep as systems note.

## Rev0013 note

This cell was added during the native-frontier pass. C++ is preferred when the inner loop is deterministic, high-volume, and framework-free; Python remains preferred for training, plotting, and orchestration.

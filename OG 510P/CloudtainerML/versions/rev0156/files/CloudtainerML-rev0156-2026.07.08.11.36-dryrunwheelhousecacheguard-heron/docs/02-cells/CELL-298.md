# CELL-298 — Spike-Sparse CPU Runtime Proxy

Priority: **P1**  
Status: `native-probe-added`

## Why this exists
experiments/spike_sparse_cpu_runtime/spike_sparse_cpu_runtime.cpp models sparse activation runtime against dense INT8 under branch/cache/fallback costs.

## Metrics
- score
- wall_proxy
- speedup_proxy
- branch_miss
- cache_miss
- quality_drop
- realized_cost

## Required baselines
- dense_int8_gemm
- naive_sparse_index
- block_sparse_fixed
- hybrid_threshold_runtime

## Stop condition
Demote if dense INT8 remains better under measured or more realistic wall proxies.

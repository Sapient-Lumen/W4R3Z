# CELL-265 — Real-Speed FLOPs Guard for Pruning Screens

Priority: **P0**  
Status: `runnable-native`  
Sources: SRC-0289, SRC-0211

## Question

Which cheap screens overstate speedup because FLOP savings fail to become GEMM/kernel/wall-time gains?

## Cheap first run

Run `experiments/real_speed_floPs_guard/real_speed_guard.cpp` and track theoretical FLOPs speedup versus wall-time proxy.

## Metrics

- `score`
- `wall_time_proxy`
- `flops_proxy`
- `quality_loss`
- `speedup_gap`

## Required baselines

- `dense_baseline`
- `unstructured_weight_prune`
- `semi_structured_2_4`
- `channel_prune_gemm_aligned`
- `dynamic_token_skip`
- `paged_sparse_attention`

## Stop condition

Make this guard mandatory if it catches screen/full reversal in native HPO sweeps.

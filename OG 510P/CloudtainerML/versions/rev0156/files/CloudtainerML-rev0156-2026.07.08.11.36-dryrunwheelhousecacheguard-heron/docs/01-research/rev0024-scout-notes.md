# rev0024 scout notes — performance-core hunt

This turn continued online research and intentionally avoided re-centering the cube on model security. The strongest new performance-first finds were:

- **STAR / MoE Routing Testbed**: subspace-aware routing plus small-scale reference routing makes MoE specialization testable before training a serious MoE.
- **Oracle-guided sparse prefill**: its best contribution for us is the gap decomposition: oracle budget gap, learned-indexer gap, and runtime realization gap.
- **Matrix/tensor decomposition diagnosis**: negative results are useful; tensorization should not be pursued unless it beats componentwise matrix baselines outside artificially shared-subspace regimes.
- **Attention sinks**: the same attention stripe can mean NOP suppression or broadcast, so intervention should be diagnostic-driven.
- **Beyond FLOPs pruning**: all pruning/sparsity screens need real-speed guardrails.

## New runnable probes

- `experiments/subspace_moe_router/subspace_moe_router.cpp`
- `experiments/oracle_sparse_prefill_gap/oracle_sparse_prefill_gap.cpp`
- `experiments/tensor_matrix_decomp_sanity/tensor_matrix_decomp_probe.cpp`
- `experiments/attention_sink_mechanism/attention_sink_probe.cpp`
- `experiments/real_speed_floPs_guard/real_speed_guard.cpp`

## Questions promoted

- Can subspace MoE routing survive rare-domain and load-balance traps?
- How much sparse-attention failure is reducibility gap versus indexer gap?
- Are tensor decompositions ever worth it under heterogeneity?
- Can sink diagnostics choose gates versus registers in a tiny trained model?
- Which native screens are most vulnerable to FLOP/wall-time reversals?

# Probe dashboard — rev0016

Probe JSON files: **120**

| Probe | Rows | File | What it is for |
|---|---:|---|---|
| kv_wind_tunnel | 78 | `artifacts/probe-results/REV0003_KV_WIND_TUNNEL_SMOKE.json` | Synthetic pseudo-decode probe; not a faithful reproduction of any specific KV quantization paper. |
| spectral_assoc_recall | 168 | `artifacts/probe-results/REV0003_SPECTRAL_ASSOC_SMOKE.json` | Synthetic continuous associative recall; not a faithful implementation of a named architecture. |
| dormant_sponsorship | 320 | `artifacts/probe-results/REV0004_DORMANT_SPONSORSHIP_SMOKE.json` | Synthetic dormant-token retention; semantic_sponsor protects value-bearing neighbors of anchors. |
| region_wipeout_cache | 240 | `artifacts/probe-results/REV0004_REGION_WIPEOUT_SMOKE.json` | Symbolic proxy for region wipe-out; success requires at least one vital token from every required region. |
| value_outlier_eviction | 216 | `artifacts/probe-results/REV0004_VALUE_OUTLIER_SMOKE.json` | Synthetic value-outlier retention and diversity probe. |
| depth_value_mixing | 240 | `artifacts/probe-results/REV0005_DEPTH_VALUE_MIXING_SMOKE.json` | Cheap geometry test for selective cross-layer value reuse. |
| dynamic_state_merging | 160 | `artifacts/probe-results/REV0005_DYNAMIC_STATE_MERGING_SMOKE.json` | Cheap simulator for content-aware bounded memory state construction. |
| entmax_support_recovery | 2016 | `artifacts/probe-results/REV0005_ENTMAX_SUPPORT_SMOKE.json` | Sparse attention turns cache selection into support recovery. Page policies should be judged by dropped mass, not just top-score recall. |
| moment_directional_gap | 2880 | `artifacts/probe-results/REV0005_MOMENT_DIRECTIONAL_SMOKE.json` | Synthetic first-order approximation of evicted-token moment correction; not a faithful MomentKV implementation. |
| qkv_projection_sharing | 750 | `artifacts/probe-results/REV0005_QKV_PROJECTION_SHARING_SMOKE.json` | Cheap falsifier for Q/K/V projection-sharing geometry; not an LM reproduction. |
| qkv_projection_sharing | None | `artifacts/probe-results/REV0005_QKV_PROJECTION_SMOKE.json` | Tiny synthetic smoke only; not a reproduction of large language-model results. |
| tensor_cache_l1_l2 | 1536 | `artifacts/probe-results/REV0005_TENSOR_CACHE_L2_SMOKE.json` | If L2 per-token writes recover old targets that sliding windows forget, Tensor Cache is worth escalating into a trainable tiny block. If chunk_mean collapses, the spuriou |
| attention_runtime_termination | 1152 | `artifacts/probe-results/REV0006_ART_RUNTIME_TERMINATION_SMOKE.json` | Early termination works when contribution order exposes important blocks before stabilization; late direction flips are the trap. |
| bank_of_values | 2400 | `artifacts/probe-results/REV0006_BANK_OF_VALUES_SMOKE.json` | BoV-like static values should win identity preservation when context drift/noise is high; context values should win when the requested attribute is truly contextual. |
| blurry_window_attention | 880 | `artifacts/probe-results/REV0006_BLURRY_WINDOW_SMOKE.json` | Bounded-memory reconstruction toy: full attention vs sliding window vs low-frequency/landmark approximations. |
| branch_cache_sharing | 336 | `artifacts/probe-results/REV0006_BRANCH_CACHE_SHARING_SMOKE.json` | Synthetic ASKS/RKSC-style cache sharing tradeoff probe: speedup vs semantic false sharing. |
| hierarchical_fademem_cache | 1260 | `artifacts/probe-results/REV0006_FADEMEM_HIERARCHY_SMOKE.json` | Cheap multiscale-cache falsifier: dense-near/sparse-far memory vs flat eviction/summarization. |
| probe_suite_dashboard | None | `artifacts/probe-results/REV0006_PROBE_SUITE_DASHBOARD.json` | Audit/refactor surface over heterogeneous CloudtainerML probe outputs. |
| probe_suite_dashboard | None | `artifacts/probe-results/REV0007_PROBE_SUITE_DASHBOARD.json` | Audit/refactor surface over heterogeneous CloudtainerML probe outputs. |
| qk_restore_amnesia | 80 | `artifacts/probe-results/REV0007_QK_RESTORE_AMNESIA_SMOKE.json` | Toy test of Q/K routing restoration after local-biased tuning damages long-range recall. |
| reasoning_wave_budget | 80 | `artifacts/probe-results/REV0007_REASONING_WAVE_BUDGET_SMOKE.json` | Synthetic per-layer/per-head decoding-time KV budget allocation test for uniform vs pyramid vs ReasonAlloc-like hierarchical routing. |
| token_precision_frontier | 80 | `artifacts/probe-results/REV0007_TOKEN_PRECISION_FRONTIER_SMOKE.json` | Equal-byte test of fewer high-precision KV tokens vs more low-precision KV tokens under synthetic cache regimes. |
| hist_window_order | 1440 | `artifacts/probe-results/REV0008_HIST_WINDOW_ORDER_SMOKE.json` | Operational positional signal from sliding-window histogram updates without explicit positional encoding. |
| intent_kv_pruning | 3072 | `artifacts/probe-results/REV0008_INTENT_KV_PRUNING_SMOKE.json` | Cross-turn intent-aware KV pruning toy with buried tool-result and stale-intent traps. |
| latent_reasoning_router | 4608 | `artifacts/probe-results/REV0008_LATENT_REASONING_ROUTER_SMOKE.json` | Cost/accuracy toy for token-wise latent-vs-explicit reasoning routers. |
| pcaf_sparse_memory | 5376 | `artifacts/probe-results/REV0008_PCAF_SPARSE_MEMORY_SMOKE.json` | Bounded hash/successor sparse memory vs full/local attention on synthetic long-context recall. |
| probe_suite_dashboard | None | `artifacts/probe-results/REV0008_PROBE_SUITE_DASHBOARD.json` | Audit/refactor surface over heterogeneous CloudtainerML probe outputs. |
| shared_routing_once | 2688 | `artifacts/probe-results/REV0008_SHARED_ROUTING_ONCE_SMOKE.json` | When can token sparse-attention routing be computed once and reused across layers? |
| forecast_sparse_routing | 18900 | `artifacts/probe-results/REV0009_FORECAST_SPARSE_ROUTING_SMOKE.json` |  |
| latent_context_compression | 400 | `artifacts/probe-results/REV0009_LATENT_CONTEXT_COMPRESSION_SMOKE.json` |  |
| observability_safe_retention | 840 | `artifacts/probe-results/REV0009_OBSERVABILITY_SAFE_RETENTION_SMOKE.json` |  |
| probe_suite_dashboard | None | `artifacts/probe-results/REV0009_PROBE_SUITE_DASHBOARD.json` | Audit/refactor surface over heterogeneous CloudtainerML probe outputs. |
| evidence_aligned_ttt | 2160 | `artifacts/probe-results/REV0010_EVIDENCE_ALIGNED_TTT_SMOKE.json` |  |
| parametric_kv_memory | 3000 | `artifacts/probe-results/REV0010_PARAMETRIC_KV_MEMORY_SMOKE.json` |  |
| probe_suite_dashboard | None | `artifacts/probe-results/REV0010_PROBE_SUITE_DASHBOARD.json` | Audit/refactor surface over heterogeneous CloudtainerML probe outputs. |
| smt_transition_training | 900 | `artifacts/probe-results/REV0010_SMT_TRANSITION_SMOKE.json` |  |
| still_compactor | 4500 | `artifacts/probe-results/REV0010_STILL_COMPACTOR_SMOKE.json` |  |
| agentic_dfs_search | 2800 | `artifacts/probe-results/REV0011_AGENTIC_DFS_SEARCH_SMOKE.json` |  |
| entropy_guided_budget | 1620 | `artifacts/probe-results/REV0011_ENTROPY_GUIDED_BUDGET_SMOKE.json` |  |
| probe_suite_dashboard | None | `artifacts/probe-results/REV0011_PROBE_SUITE_DASHBOARD.json` | Audit/refactor surface over heterogeneous CloudtainerML probe outputs. |
| reasoning_cache_share_exit | 1890 | `artifacts/probe-results/REV0011_REASONING_CACHE_SHARE_EXIT_SMOKE.json` |  |
| centaur_hpo_state_smoke | 20 | `artifacts/probe-results/REV0012_CENTAUR_HPO_STATE_SMOKE.json` |  |
| clp_multitoken_acceptance_smoke | 16 | `artifacts/probe-results/REV0012_CLP_MULTITOKEN_ACCEPTANCE_SMOKE.json` |  |
| express_streaming_coreset_cpp_smoke | 64 | `artifacts/probe-results/REV0012_EXPRESS_STREAMING_CORESET_SMOKE.json` |  |
| probe_suite_dashboard | None | `artifacts/probe-results/REV0012_PROBE_SUITE_DASHBOARD.json` | Audit/refactor surface over heterogeneous CloudtainerML probe outputs. |
| trace_prefix_rollout_smoke | 48 | `artifacts/probe-results/REV0012_TRACE_PREFIX_ROLLOUT_SMOKE.json` |  |
| centaur_hpo_state_smoke | 20 | `artifacts/probe-results/REV0013_CENTAUR_HPO_STATE_SMOKE.json` |  |
| clp_multitoken_acceptance_smoke | 16 | `artifacts/probe-results/REV0013_CLP_MULTITOKEN_ACCEPTANCE_SMOKE.json` |  |
| express_streaming_coreset_cpp_smoke | 64 | `artifacts/probe-results/REV0013_EXPRESS_STREAMING_CORESET_SMOKE.json` |  |
| gated_delta_memory | 15 | `artifacts/probe-results/REV0013_GATED_DELTA_MEMORY_SMOKE.json` |  |
| kvcat_compressibility | 192 | `artifacts/probe-results/REV0013_KVCAT_COMPRESSIBILITY_SMOKE.json` |  |
| lrkv_head_diversity | 35 | `artifacts/probe-results/REV0013_LRKV_HEAD_DIVERSITY_SMOKE.json` |  |
| native_token_precision_frontier | 105 | `artifacts/probe-results/REV0013_NATIVE_TOKEN_PRECISION_FRONTIER_SMOKE.json` |  |
| probe_suite_dashboard | None | `artifacts/probe-results/REV0013_PROBE_SUITE_DASHBOARD.json` | Audit/refactor surface over heterogeneous CloudtainerML probe outputs. |
| query_move_cache_cost | 864 | `artifacts/probe-results/REV0013_QUERY_MOVE_CACHE_SMOKE.json` |  |
| query_move_phase_boundary | 4608 | `artifacts/probe-results/REV0013_QUERY_MOVE_PHASE_SCAN_SMOKE.json` |  |
| native_residual_kv_sensitivity | 300 | `artifacts/probe-results/REV0013_RESIDUAL_KV_SENSITIVITY_SMOKE.json` |  |
| residual_stream_kv | 108 | `artifacts/probe-results/REV0013_RESIDUAL_STREAM_KV_SMOKE.json` |  |
| trace_prefix_rollout_smoke | 48 | `artifacts/probe-results/REV0013_TRACE_PREFIX_ROLLOUT_SMOKE.json` |  |
| express_streaming_coreset_cpp_smoke | 64 | `artifacts/probe-results/REV0014_EXPRESS_STREAMING_CORESET_SMOKE.json` |  |
| gated_delta_memory | 15 | `artifacts/probe-results/REV0014_GATED_DELTA_MEMORY_SMOKE.json` |  |
| kvcat_compressibility | 192 | `artifacts/probe-results/REV0014_KVCAT_COMPRESSIBILITY_SMOKE.json` |  |
| lrkv_head_diversity | 35 | `artifacts/probe-results/REV0014_LRKV_HEAD_DIVERSITY_SMOKE.json` |  |
| native_token_precision_frontier | 105 | `artifacts/probe-results/REV0014_NATIVE_TOKEN_PRECISION_FRONTIER_SMOKE.json` |  |
| probe_suite_dashboard | None | `artifacts/probe-results/REV0014_PROBE_SUITE_DASHBOARD.json` | Audit/refactor surface over heterogeneous CloudtainerML probe outputs. |
| query_move_cache_cost | 864 | `artifacts/probe-results/REV0014_QUERY_MOVE_CACHE_SMOKE.json` |  |
| query_move_phase_boundary | 4608 | `artifacts/probe-results/REV0014_QUERY_MOVE_PHASE_SCAN_SMOKE.json` |  |
| native_residual_kv_sensitivity | 300 | `artifacts/probe-results/REV0014_RESIDUAL_KV_SENSITIVITY_SMOKE.json` |  |
| residual_stream_kv | 108 | `artifacts/probe-results/REV0014_RESIDUAL_STREAM_KV_SMOKE.json` |  |
| stochastic_sparse_attention | 240 | `artifacts/probe-results/REV0014_STOCHASTIC_SPARSE_ATTENTION_SMOKE.json` |  |
| dfssm_quant_scaffold | 28 | `artifacts/probe-results/REV0015_DFSSM_QUANT_SCAFFOLD_SMOKE.json` |  |
| express_streaming_coreset_cpp_smoke | 64 | `artifacts/probe-results/REV0015_EXPRESS_STREAMING_CORESET_SMOKE.json` |  |
| gated_delta_memory | 15 | `artifacts/probe-results/REV0015_GATED_DELTA_MEMORY_SMOKE.json` |  |
| hypergraph_memory_trace | 120 | `artifacts/probe-results/REV0015_HYPERGRAPH_MEMORY_TRACE_SMOKE.json` |  |
| kvcat_compressibility | 192 | `artifacts/probe-results/REV0015_KVCAT_COMPRESSIBILITY_SMOKE.json` |  |
| lrkv_head_diversity | 35 | `artifacts/probe-results/REV0015_LRKV_HEAD_DIVERSITY_SMOKE.json` |  |
| memory_sycophancy_trap | 96 | `artifacts/probe-results/REV0015_MEMORY_SYCOPHANCY_TRAP_SMOKE.json` |  |
| native_hpo_phase | 80 | `artifacts/probe-results/REV0015_NATIVE_HPO_PHASE_SMOKE.json` |  |
| native_token_precision_frontier | 105 | `artifacts/probe-results/REV0015_NATIVE_TOKEN_PRECISION_FRONTIER_SMOKE.json` |  |
| probe_suite_dashboard | None | `artifacts/probe-results/REV0015_PROBE_SUITE_DASHBOARD.json` | Audit/refactor surface over heterogeneous CloudtainerML probe outputs. |
| query_move_cache_cost | 864 | `artifacts/probe-results/REV0015_QUERY_MOVE_CACHE_SMOKE.json` |  |
| query_move_phase_boundary | 4608 | `artifacts/probe-results/REV0015_QUERY_MOVE_PHASE_SCAN_SMOKE.json` |  |
| native_residual_kv_sensitivity | 300 | `artifacts/probe-results/REV0015_RESIDUAL_KV_SENSITIVITY_SMOKE.json` |  |
| residual_stream_kv | 108 | `artifacts/probe-results/REV0015_RESIDUAL_STREAM_KV_SMOKE.json` |  |
| stochastic_sparse_attention | 240 | `artifacts/probe-results/REV0015_STOCHASTIC_SPARSE_ATTENTION_SMOKE.json` |  |
| dfssm_quant_scaffold | 28 | `artifacts/probe-results/REV0016_DFSSM_QUANT_SCAFFOLD_SMOKE.json` |  |
| express_streaming_coreset_cpp_smoke | 64 | `artifacts/probe-results/REV0016_EXPRESS_STREAMING_CORESET_SMOKE.json` |  |
| gated_delta_memory | 15 | `artifacts/probe-results/REV0016_GATED_DELTA_MEMORY_SMOKE.json` |  |
| hypergraph_memory_trace | 120 | `artifacts/probe-results/REV0016_HYPERGRAPH_MEMORY_TRACE_SMOKE.json` |  |
| kvcat_compressibility | 192 | `artifacts/probe-results/REV0016_KVCAT_COMPRESSIBILITY_SMOKE.json` |  |
| lrkv_head_diversity | 35 | `artifacts/probe-results/REV0016_LRKV_HEAD_DIVERSITY_SMOKE.json` |  |
| memory_provenance_phase | 336 | `artifacts/probe-results/REV0016_MEMORY_PROVENANCE_PHASE_SMOKE.json` |  |
| memory_sycophancy_trap | 96 | `artifacts/probe-results/REV0016_MEMORY_SYCOPHANCY_TRAP_SMOKE.json` |  |
| native_hpo_phase | 80 | `artifacts/probe-results/REV0016_NATIVE_HPO_PHASE_SMOKE.json` |  |
| native_token_precision_frontier | 105 | `artifacts/probe-results/REV0016_NATIVE_TOKEN_PRECISION_FRONTIER_SMOKE.json` |  |
| periodic_cache_rewrite | 25 | `artifacts/probe-results/REV0016_PERIODIC_CACHE_REWRITE_SMOKE.json` |  |
| probe_suite_dashboard | None | `artifacts/probe-results/REV0016_PROBE_SUITE_DASHBOARD.json` | Audit/refactor surface over heterogeneous CloudtainerML probe outputs. |
| query_move_cache_cost | 864 | `artifacts/probe-results/REV0016_QUERY_MOVE_CACHE_SMOKE.json` |  |
| query_move_phase_boundary | 4608 | `artifacts/probe-results/REV0016_QUERY_MOVE_PHASE_SCAN_SMOKE.json` |  |
| native_residual_kv_sensitivity | 300 | `artifacts/probe-results/REV0016_RESIDUAL_KV_SENSITIVITY_SMOKE.json` |  |
| residual_stream_kv | 108 | `artifacts/probe-results/REV0016_RESIDUAL_STREAM_KV_SMOKE.json` |  |
| stochastic_sparse_attention | 240 | `artifacts/probe-results/REV0016_STOCHASTIC_SPARSE_ATTENTION_SMOKE.json` |  |
| dfssm_quant_scaffold | 28 | `artifacts/probe-results/REV0016_TEST2_dfssm_quant_probe.json` |  |
| express_streaming_coreset_cpp_smoke | 64 | `artifacts/probe-results/REV0016_TEST2_express_coreset.json` |  |
| gated_delta_memory | 15 | `artifacts/probe-results/REV0016_TEST2_gated_delta_memory_probe.json` |  |
| hypergraph_memory_trace | 120 | `artifacts/probe-results/REV0016_TEST2_hypergraph_trace_probe.json` |  |
| native_token_precision_frontier | 105 | `artifacts/probe-results/REV0016_TEST2_token_precision_frontier.json` |  |
| dfssm_quant_scaffold | 28 | `artifacts/probe-results/REV0016_TEST_dfssm_quant_probe.json` |  |
| express_streaming_coreset_cpp_smoke | 64 | `artifacts/probe-results/REV0016_TEST_express_coreset.json` |  |
| gated_delta_memory | 15 | `artifacts/probe-results/REV0016_TEST_gated_delta_memory_probe.json` |  |
| hypergraph_memory_trace | 120 | `artifacts/probe-results/REV0016_TEST_hypergraph_trace_probe.json` |  |
| kvcat_compressibility | 192 | `artifacts/probe-results/REV0016_TEST_kvcat_compressibility.json` |  |
| lrkv_head_diversity | 35 | `artifacts/probe-results/REV0016_TEST_lrkv_head_diversity.json` |  |
| memory_provenance_phase | 336 | `artifacts/probe-results/REV0016_TEST_memory_provenance_phase.json` |  |
| memory_sycophancy_trap | 96 | `artifacts/probe-results/REV0016_TEST_memory_sycophancy_probe.json` |  |
| native_hpo_phase | 80 | `artifacts/probe-results/REV0016_TEST_native_hpo_phase.json` |  |
| native_residual_kv_sensitivity | 300 | `artifacts/probe-results/REV0016_TEST_residual_kv_sensitivity.json` |  |
| native_token_precision_frontier | 105 | `artifacts/probe-results/REV0016_TEST_token_precision_frontier.json` |  |
| vericache_guard | 35 | `artifacts/probe-results/REV0016_VERICACHE_GUARD_SMOKE.json` |  |
| native_token_precision_frontier | 105 | `artifacts/probe-results/foo.json` |  |

## Notes

- This dashboard is intentionally shallow: it verifies that probe outputs are discoverable and comparable before deeper plotting exists.
- Next refactor target: normalize metric names across probes so cross-probe charts can be generated automatically.

# Native C++ probe index — rev0016

C++ probes: **17**
Compiled in audit: **17**

| source | lines | probe | rows | metric | note |
|---|---:|---|---:|---|---|
| `experiments/dfssm_quant_scaffold/dfssm_quant_probe.cpp` | 30 | dfssm_quant_scaffold | 28 | mean_rel_state_error / lower_is_better | CloudtainerML rev0016: 1-bit scaffold + low-rank correction probe for SSM-like transitions. |
| `experiments/express_streaming_coreset/express_coreset.cpp` | 272 | express_streaming_coreset_cpp_smoke | 64 | mean_mse_to_full_attention / lower_is_better | CloudtainerML rev0016: Express-style streaming coreset toy probe. |
| `experiments/gated_delta_memory/gated_delta_memory_probe.cpp` | 38 | gated_delta_memory | 15 | mean_retrieval_rel_error / lower_is_better | CloudtainerML rev0016: decoupled erase/write fast-weight memory probe. |
| `experiments/hypergraph_memory_trace/hypergraph_trace_probe.cpp` | 47 | hypergraph_memory_trace | 120 | success_rate / higher_is_better | CloudtainerML rev0016: structure-aware on-demand hypergraph memory probe. |
| `experiments/kvcat_compressibility/kvcat_compressibility.cpp` | 79 | kvcat_compressibility | 192 | score / lower_is_better | CloudtainerML rev0016: carried-forward native probe, current-revision emission. |
| `experiments/lrkv_head_diversity/lrkv_head_diversity.cpp` | 82 | lrkv_head_diversity | 35 | score / lower_is_better | CloudtainerML rev0016: carried-forward native probe, current-revision emission. |
| `experiments/memory_provenance_phase/memory_provenance_phase.cpp` | 86 | memory_provenance_phase | 336 | mean_utility / higher_is_better | CloudtainerML rev0016: persistent-memory provenance phase sweep. |
| `experiments/memory_sycophancy_trap/memory_sycophancy_probe.cpp` | 31 | memory_sycophancy_trap | 96 | sycophancy_rate / lower_is_better | CloudtainerML rev0016: memory sycophancy / lossy-snippet trap. |
| `experiments/native_hpo_phase/native_hpo_phase.cpp` | 107 | native_hpo_phase | 80 | mean_regret_to_dense_grid_optimum / lower_is_better | CloudtainerML rev0016: native phase-boundary optimizer probe. |
| `experiments/native_residual_kv_sensitivity/residual_kv_sensitivity.cpp` | 124 | native_residual_kv_sensitivity | 300 | score / lower_is_better | CloudtainerML rev0016: carried-forward native probe, current-revision emission. |
| `experiments/native_token_precision_frontier/token_precision_frontier.cpp` | 127 | native_token_precision_frontier | 105 | mean_output_rel_error / lower_is_better | CloudtainerML rev0016: native token-vs-precision KV cache frontier probe. |
| `experiments/periodic_cache_rewrite/step_rewrite_probe.cpp` | 84 | periodic_cache_rewrite | 25 | mean_utility / higher_is_better | CloudtainerML rev0016: periodic/step-boundary cache rewrite probe. |
| `experiments/query_move_cache/query_move_probe.cpp` | 37 | query_move_cache_cost | 864 | estimated_us / lower_is_better | CloudtainerML rev0016: move-the-query versus move-the-cache cost model. |
| `experiments/query_move_phase_boundary/query_move_phase_scan.cpp` | 62 | query_move_phase_boundary | 4608 | latency_us / lower_is_better | CloudtainerML rev0016: carried-forward native probe, current-revision emission. |
| `experiments/residual_stream_kv/residual_stream_kv.cpp` | 45 | residual_stream_kv | 108 | state_mb / lower_is_better | CloudtainerML rev0016: residual-stream versus full-KV cache object probe. |
| `experiments/stochastic_sparse_attention/stochastic_sparse_attention.cpp` | 76 | stochastic_sparse_attention | 240 | score / lower_is_better | CloudtainerML rev0016: carried-forward native probe, current-revision emission. |
| `experiments/vericache_guard/vericache_guard_probe.cpp` | 104 | vericache_guard | 35 | mean_utility / higher_is_better | CloudtainerML rev0016: VeriCache-style guard wind tunnel. |

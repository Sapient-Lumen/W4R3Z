# Native family report — rev0016

- native outputs: 17

| output | probe | rows | primary metric | winners |
|---|---:|---:|---|---|
| `artifacts/probe-results/REV0016_DFSSM_QUANT_SCAFFOLD_SMOKE.json` | dfssm_quant_scaffold | 28 | mean_rel_state_error / lower_is_better |  |
| `artifacts/probe-results/REV0016_EXPRESS_STREAMING_CORESET_SMOKE.json` | express_streaming_coreset_cpp_smoke | 64 | mean_mse_to_full_attention / lower_is_better |  |
| `artifacts/probe-results/REV0016_GATED_DELTA_MEMORY_SMOKE.json` | gated_delta_memory | 15 | mean_retrieval_rel_error / lower_is_better | tied_scalar_delta:3 |
| `artifacts/probe-results/REV0016_HYPERGRAPH_MEMORY_TRACE_SMOKE.json` | hypergraph_memory_trace | 120 | success_rate / higher_is_better | oracle_evidence:1261; hierarchy_sections_then_local:15; hypergraph_trace:4 |
| `artifacts/probe-results/REV0016_KVCAT_COMPRESSIBILITY_SMOKE.json` | kvcat_compressibility | 192 | score / lower_is_better | kvcat_like_clustered/cluster_prototype:26; kvcat_like_clustered/uniform_thin:4; base_isotropic/importance_needle_aware:1; kvcat_like_clustered/importance_needle_aware:1 |
| `artifacts/probe-results/REV0016_LRKV_HEAD_DIVERSITY_SMOKE.json` | lrkv_head_diversity | 35 | score / lower_is_better | full_mha:3; lrkv_residual_rank4:2 |
| `artifacts/probe-results/REV0016_MEMORY_PROVENANCE_PHASE_SMOKE.json` | memory_provenance_phase | 336 | mean_utility / higher_is_better | oracle_provenance:960 |
| `artifacts/probe-results/REV0016_MEMORY_SYCOPHANCY_TRAP_SMOKE.json` | memory_sycophancy_trap | 96 | sycophancy_rate / lower_is_better |  |
| `artifacts/probe-results/REV0016_NATIVE_HPO_PHASE_SMOKE.json` | native_hpo_phase | 80 | mean_regret_to_dense_grid_optimum / lower_is_better | domain_prior:85; grid:60; random:46; centaur_state_prior:35; cross_entropy:30 |
| `artifacts/probe-results/REV0016_NATIVE_TOKEN_PRECISION_FRONTIER_SMOKE.json` | native_token_precision_frontier | 105 | mean_output_rel_error / lower_is_better | mixed_8_4_2:5; few_8bit_attention:4; many_2bit_attention:3; more_4bit_attention:3 |
| `artifacts/probe-results/REV0016_PERIODIC_CACHE_REWRITE_SMOKE.json` | periodic_cache_rewrite | 25 | mean_utility / higher_is_better | oracle_step_rewrite:379; attention_reconsolidate:99; step_boundary_rewrite:2 |
| `artifacts/probe-results/REV0016_QUERY_MOVE_CACHE_SMOKE.json` | query_move_cache_cost | 864 | estimated_us / lower_is_better | move_query:236; recompute_local:52 |
| `artifacts/probe-results/REV0016_QUERY_MOVE_PHASE_SCAN_SMOKE.json` | query_move_phase_boundary | 4608 | latency_us / lower_is_better | index_then_fetch:746; move_query:262; recompute_local:144 |
| `artifacts/probe-results/REV0016_RESIDUAL_KV_SENSITIVITY_SMOKE.json` | native_residual_kv_sensitivity | 300 | score / lower_is_better | residual_checkpoint_recompute:48; lowrank_residual_sketch:12 |
| `artifacts/probe-results/REV0016_RESIDUAL_STREAM_KV_SMOKE.json` | residual_stream_kv | 108 | state_mb / lower_is_better |  |
| `artifacts/probe-results/REV0016_STOCHASTIC_SPARSE_ATTENTION_SMOKE.json` | stochastic_sparse_attention | 240 | score / lower_is_better | stratified_mc:38; santa_postsoftmax_mc:17; topk_renorm:3; value_aware_topk:2 |
| `artifacts/probe-results/REV0016_VERICACHE_GUARD_SMOKE.json` | vericache_guard | 35 | mean_utility / higher_is_better | oracle_risk_guard:400 |

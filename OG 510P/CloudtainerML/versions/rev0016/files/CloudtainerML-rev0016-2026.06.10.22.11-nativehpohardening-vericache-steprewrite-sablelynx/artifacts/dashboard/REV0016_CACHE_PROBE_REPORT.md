# Cache/memory probe report — rev0016

Artifacts: **108**
Schema-ready: **108**

## Family counts

- **agentic budget**: 2 artifacts; 2 schema-ready
- **agentic search**: 1 artifacts; 1 schema-ready
- **attention architecture**: 12 artifacts; 12 schema-ready
- **bounded memory**: 18 artifacts; 18 schema-ready
- **decoding acceleration**: 2 artifacts; 2 schema-ready
- **meta optimization**: 5 artifacts; 5 schema-ready
- **other**: 17 artifacts; 17 schema-ready
- **quantization**: 17 artifacts; 17 schema-ready
- **retention/eviction**: 6 artifacts; 6 schema-ready
- **routing/indexing**: 19 artifacts; 19 schema-ready
- **runtime/depth**: 2 artifacts; 2 schema-ready
- **streaming coreset**: 7 artifacts; 7 schema-ready

## Compact winners

| family | probe | rows | metric | compact result |
|---|---|---:|---|---|
| quantization | kv_wind_tunnel | 78 | relative_error |  |
| bounded memory | spectral_assoc_recall | 168 | accuracy |  |
| retention/eviction | dormant_sponsorship | 320 | target_value_retention |  |
| retention/eviction | region_wipeout_cache | 240 | coverage_success |  |
| retention/eviction | value_outlier_eviction | 216 | critical_value_retention |  |
| attention architecture | depth_value_mixing | 240 | mean_error |  |
| bounded memory | dynamic_state_merging | 160 | transition_preservation |  |
| attention architecture | entmax_support_recovery | 0 | output_error |  |
| retention/eviction | moment_directional_gap | 2880 | reconstruction_error |  |
| attention architecture | qkv_projection_sharing | 750 | relative_error |  |
| attention architecture | qkv_projection_sharing | 0 | relative_error |  |
| bounded memory | tensor_cache_l1_l2 | 0 | retrieval_error |  |
| runtime/depth | attention_runtime_termination | 0 | relative_error |  |
| attention architecture | bank_of_values | 0 | prediction_accuracy |  |
| bounded memory | blurry_window_attention | 880 | reconstruction_error |  |
| routing/indexing | branch_cache_sharing | 336 | state_match |  |
| bounded memory | hierarchical_fademem_cache | 1260 | reconstruction_error |  |
| attention architecture | qk_restore_amnesia | 80 | recall_accuracy | qk_restore:3 |
| routing/indexing | reasoning_wave_budget | 80 | retained_mass | oracle_step:3 |
| quantization | token_precision_frontier | 80 | quality_score | mixed_salience_8_4_2:7; few_8bit_attention:5; many_2bit_attention:1; more_4bit_attention:1; semantic_sponsor_4bit:1 |
| attention architecture | hist_window_order | 1440 | outgoing_accuracy | delta_exact:4 |
| retention/eviction | intent_kv_pruning | 3072 | critical_retention_purity_minus_stale_error | oracle_critical:4 |
| runtime/depth | latent_reasoning_router | 4608 | utility | oracle_router:2; all_flow_latent:1; all_latent:1 |
| routing/indexing | pcaf_sparse_memory | 5376 | mean_exact_success_minus_error_cost | semantic_topk_oracle:4 |
| routing/indexing | shared_routing_once | 2688 | support_recall_minus_bad_layers_and_cost | per_layer_score:3; consensus_shared:1 |
| routing/indexing | forecast_sparse_routing | 18900 | mass_recall | forecast_next_layer:15 |
| bounded memory | latent_context_compression | 400 | output_rel_error | compressed_then_expand_top2:4; random_expand_top1:1 |
| retention/eviction | observability_safe_retention | 840 | score | stale_averse:7; recency:3; risk_aware_oas:3; online_salience:2 |
| routing/indexing | evidence_aligned_ttt | 2160 | answer_accuracy | ease_ttt_softmix:12; ease_ttt_topk:10; full_context_base:9; retrieval_only_topk:9; random_qttt:5 |
| bounded memory | parametric_kv_memory | 3000 | rouge_l_proxy | adapter_when_cache_miss:15; context_only:5; adapter_only:4; gated_context_adapter:1 |
| bounded memory | smt_transition_training | 900 | query_accuracy | ridge_supervised_update:15 |
| bounded memory | still_compactor | 4500 | reconstruction_error | centroid_slots:23; attention_topk:4; hybrid_latent_plus_topk:3 |
| agentic search | agentic_dfs_search | 2800 | efficiency | dfs_two_head:19; random_walk:1 |
| routing/indexing | entropy_guided_budget | 1620 | weighted_utility | entropy_plus_decode:15 |
| routing/indexing | reasoning_cache_share_exit | 1890 | utility | oracle_cluster_exit:15 |
| meta optimization | centaur_hpo_state_smoke | 20 | mean_best_score |  |
| decoding acceleration | clp_multitoken_acceptance_smoke | 16 | speed_quality_utility |  |
| streaming coreset | express_streaming_coreset_cpp_smoke | 64 | mean_mse_to_full_attention |  |
| agentic budget | trace_prefix_rollout_smoke | 48 | mean_reward_contrast |  |
| meta optimization | centaur_hpo_state_smoke | 20 | mean_best_score |  |
| decoding acceleration | clp_multitoken_acceptance_smoke | 16 | speed_quality_utility |  |
| streaming coreset | express_streaming_coreset_cpp_smoke | 64 | mean_mse_to_full_attention |  |
| other | gated_delta_memory | 15 | mean_retrieval_rel_error | tied_scalar_delta:3 |
| quantization | kvcat_compressibility | 192 | score | kvcat_like_clustered/cluster_prototype:26; kvcat_like_clustered/uniform_thin:4; base_isotropic/importance_needle_aware:1; kvcat_like_clustered/importance_needle_aware:1 |
| attention architecture | lrkv_head_diversity | 35 | score | full_mha:3; lrkv_residual_rank4:2 |
| quantization | native_token_precision_frontier | 105 | mean_output_rel_error | mixed_8_4_2:5; few_8bit_attention:4; many_2bit_attention:3; more_4bit_attention:3 |
| routing/indexing | query_move_cache_cost | 864 | estimated_us | move_query:236; recompute_local:52 |
| routing/indexing | query_move_phase_boundary | 4608 | latency_us | index_then_fetch:746; move_query:262; recompute_local:144 |
| bounded memory | native_residual_kv_sensitivity | 300 | score | residual_checkpoint_recompute:48; lowrank_residual_sketch:12 |
| bounded memory | residual_stream_kv | 108 | state_mb |  |
| agentic budget | trace_prefix_rollout_smoke | 48 | mean_reward_contrast |  |
| streaming coreset | express_streaming_coreset_cpp_smoke | 64 | mean_mse_to_full_attention |  |
| other | gated_delta_memory | 15 | mean_retrieval_rel_error | tied_scalar_delta:3 |
| quantization | kvcat_compressibility | 192 | score | kvcat_like_clustered/cluster_prototype:26; kvcat_like_clustered/uniform_thin:4; base_isotropic/importance_needle_aware:1; kvcat_like_clustered/importance_needle_aware:1 |
| attention architecture | lrkv_head_diversity | 35 | score | full_mha:3; lrkv_residual_rank4:2 |
| quantization | native_token_precision_frontier | 105 | mean_output_rel_error | mixed_8_4_2:5; few_8bit_attention:4; many_2bit_attention:3; more_4bit_attention:3 |
| routing/indexing | query_move_cache_cost | 864 | estimated_us | move_query:236; recompute_local:52 |
| routing/indexing | query_move_phase_boundary | 4608 | latency_us | index_then_fetch:746; move_query:262; recompute_local:144 |
| bounded memory | native_residual_kv_sensitivity | 300 | score | residual_checkpoint_recompute:48; lowrank_residual_sketch:12 |
| bounded memory | residual_stream_kv | 108 | state_mb |  |
| routing/indexing | stochastic_sparse_attention | 240 | score | stratified_mc:38; santa_postsoftmax_mc:17; topk_renorm:3; value_aware_topk:2 |
| quantization | dfssm_quant_scaffold | 28 | mean_rel_state_error |  |
| streaming coreset | express_streaming_coreset_cpp_smoke | 64 | mean_mse_to_full_attention |  |
| other | gated_delta_memory | 15 | mean_retrieval_rel_error | tied_scalar_delta:3 |
| other | hypergraph_memory_trace | 120 | success_rate | oracle_evidence:1261; hierarchy_sections_then_local:15; hypergraph_trace:4 |
| quantization | kvcat_compressibility | 192 | score | kvcat_like_clustered/cluster_prototype:26; kvcat_like_clustered/uniform_thin:4; base_isotropic/importance_needle_aware:1; kvcat_like_clustered/importance_needle_aware:1 |
| attention architecture | lrkv_head_diversity | 35 | score | full_mha:3; lrkv_residual_rank4:2 |
| other | memory_sycophancy_trap | 96 | sycophancy_rate |  |
| meta optimization | native_hpo_phase | 80 | mean_regret_to_dense_grid_optimum | domain_prior:85; grid:60; random:46; centaur_state_prior:35; cross_entropy:30 |
| quantization | native_token_precision_frontier | 105 | mean_output_rel_error | mixed_8_4_2:5; few_8bit_attention:4; many_2bit_attention:3; more_4bit_attention:3 |
| routing/indexing | query_move_cache_cost | 864 | estimated_us | move_query:236; recompute_local:52 |
| routing/indexing | query_move_phase_boundary | 4608 | latency_us | index_then_fetch:746; move_query:262; recompute_local:144 |
| bounded memory | native_residual_kv_sensitivity | 300 | score | residual_checkpoint_recompute:48; lowrank_residual_sketch:12 |
| bounded memory | residual_stream_kv | 108 | state_mb |  |
| routing/indexing | stochastic_sparse_attention | 240 | score | stratified_mc:38; santa_postsoftmax_mc:17; topk_renorm:3; value_aware_topk:2 |
| quantization | dfssm_quant_scaffold | 28 | mean_rel_state_error |  |
| streaming coreset | express_streaming_coreset_cpp_smoke | 64 | mean_mse_to_full_attention |  |
| other | gated_delta_memory | 15 | mean_retrieval_rel_error | tied_scalar_delta:3 |
| other | hypergraph_memory_trace | 120 | success_rate | oracle_evidence:1261; hierarchy_sections_then_local:15; hypergraph_trace:4 |
| quantization | kvcat_compressibility | 192 | score | kvcat_like_clustered/cluster_prototype:26; kvcat_like_clustered/uniform_thin:4; base_isotropic/importance_needle_aware:1; kvcat_like_clustered/importance_needle_aware:1 |
| attention architecture | lrkv_head_diversity | 35 | score | full_mha:3; lrkv_residual_rank4:2 |
| other | memory_provenance_phase | 336 | mean_utility | correction_linked_memory:746; provenance_balanced_memory:188; skeptical_highstakes_memory:19; belief_snippet_memory:7 |
| other | memory_sycophancy_trap | 96 | sycophancy_rate |  |
| meta optimization | native_hpo_phase | 80 | mean_regret_to_dense_grid_optimum | domain_prior:85; grid:60; random:46; centaur_state_prior:35; cross_entropy:30 |
| quantization | native_token_precision_frontier | 105 | mean_output_rel_error | mixed_8_4_2:5; few_8bit_attention:4; many_2bit_attention:3; more_4bit_attention:3 |
| other | periodic_cache_rewrite | 25 | mean_utility | attention_reconsolidate:334; continuous_eviction:113; fixed_periodic_rewrite:19; step_boundary_rewrite:14 |
| routing/indexing | query_move_cache_cost | 864 | estimated_us | move_query:236; recompute_local:52 |
| routing/indexing | query_move_phase_boundary | 4608 | latency_us | index_then_fetch:746; move_query:262; recompute_local:144 |
| bounded memory | native_residual_kv_sensitivity | 300 | score | residual_checkpoint_recompute:48; lowrank_residual_sketch:12 |
| bounded memory | residual_stream_kv | 108 | state_mb |  |
| routing/indexing | stochastic_sparse_attention | 240 | score | stratified_mc:38; santa_postsoftmax_mc:17; topk_renorm:3; value_aware_topk:2 |
| quantization | dfssm_quant_scaffold | 28 | mean_rel_state_error |  |
| streaming coreset | express_streaming_coreset_cpp_smoke | 64 | mean_mse_to_full_attention |  |
| other | gated_delta_memory | 15 | mean_retrieval_rel_error | tied_scalar_delta:3 |
| other | hypergraph_memory_trace | 120 | success_rate | oracle_evidence:1261; hierarchy_sections_then_local:15; hypergraph_trace:4 |
| quantization | native_token_precision_frontier | 105 | mean_output_rel_error | mixed_8_4_2:5; few_8bit_attention:4; many_2bit_attention:3; more_4bit_attention:3 |
| quantization | dfssm_quant_scaffold | 28 | mean_rel_state_error |  |
| streaming coreset | express_streaming_coreset_cpp_smoke | 64 | mean_mse_to_full_attention |  |
| other | gated_delta_memory | 15 | mean_retrieval_rel_error | tied_scalar_delta:3 |
| other | hypergraph_memory_trace | 120 | success_rate | oracle_evidence:1261; hierarchy_sections_then_local:15; hypergraph_trace:4 |
| quantization | kvcat_compressibility | 192 | score | kvcat_like_clustered/cluster_prototype:26; kvcat_like_clustered/uniform_thin:4; base_isotropic/importance_needle_aware:1; kvcat_like_clustered/importance_needle_aware:1 |
| attention architecture | lrkv_head_diversity | 35 | score | full_mha:3; lrkv_residual_rank4:2 |
| other | memory_provenance_phase | 336 | mean_utility | correction_linked_memory:746; provenance_balanced_memory:188; skeptical_highstakes_memory:19; belief_snippet_memory:7 |
| other | memory_sycophancy_trap | 96 | sycophancy_rate |  |
| meta optimization | native_hpo_phase | 80 | mean_regret_to_dense_grid_optimum | domain_prior:85; grid:60; random:46; centaur_state_prior:35; cross_entropy:30 |
| bounded memory | native_residual_kv_sensitivity | 300 | score | residual_checkpoint_recompute:48; lowrank_residual_sketch:12 |
| quantization | native_token_precision_frontier | 105 | mean_output_rel_error | mixed_8_4_2:5; few_8bit_attention:4; many_2bit_attention:3; more_4bit_attention:3 |
| other | vericache_guard | 35 | mean_utility | full_kv:237; vericache_toy_guard:163 |

## Audit note

This report is deliberately a comparison surface, not a unified leaderboard. The next refactor should add per-family comparable metrics and graph specs.

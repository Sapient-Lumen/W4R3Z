# Probe metric index — rev0016

Artifacts: **108**
Metric-ready: **108**
Needs schema patch: **0**

| probe | rows | status | metric | winners / compact result |
|---|---:|---|---|---|
| kv_wind_tunnel | 78 | declared | relative_error |  |
| spectral_assoc_recall | 168 | declared | accuracy |  |
| dormant_sponsorship | 320 | declared | target_value_retention |  |
| region_wipeout_cache | 240 | declared | coverage_success |  |
| value_outlier_eviction | 216 | declared | critical_value_retention |  |
| depth_value_mixing | 240 | declared | mean_error |  |
| dynamic_state_merging | 160 | declared | transition_preservation |  |
| entmax_support_recovery | 2016 | declared | output_error |  |
| moment_directional_gap | 2880 | declared | reconstruction_error |  |
| qkv_projection_sharing | 750 | declared | relative_error |  |
| qkv_projection_sharing | 0 | declared | relative_error |  |
| tensor_cache_l1_l2 | 1536 | declared | retrieval_error |  |
| attention_runtime_termination | 1152 | declared | relative_error |  |
| bank_of_values | 2400 | declared | prediction_accuracy |  |
| blurry_window_attention | 880 | declared | reconstruction_error |  |
| branch_cache_sharing | 336 | declared | state_match |  |
| hierarchical_fademem_cache | 1260 | declared | reconstruction_error | full_cache:15 |
| qk_restore_amnesia | 80 | declared | recall_accuracy | clean_recall:pre_sft_qk; cot_local_bias:pre_sft_qk; hard_decoy:pre_sft_qk |
| reasoning_wave_budget | 80 | declared | retained_mass |  |
| token_precision_frontier | 80 | declared | quality_score |  |
| hist_window_order | 1440 | declared | outgoing_accuracy | adversarial_same_hist:delta_exact; bursty_runs:delta_exact; iid_balanced:delta_exact; low_entropy_cycles:delta_exact |
| intent_kv_pruning | 3072 | declared | critical_retention_purity_minus_stale_error | adversarial_recent_noise:oracle_critical; buried_tool_result:oracle_critical; intent_shift:oracle_critical; stable_intent:oracle_critical |
| latent_reasoning_router | 4608 | declared | utility | easy_smooth:all_flow_latent; hard_spikes:oracle_router; late_brittle:oracle_router; uncertain_but_latent_good:all_latent |
| pcaf_sparse_memory | 5376 | declared | mean_exact_success_minus_error_cost | clean_old_successor:semantic_topk_oracle; noisy_bucket_collision:semantic_topk_oracle; rare_old_fact_vs_recent_noise:semantic_topk_oracle; recurring_entity_update:semantic_topk_oracle |
| shared_routing_once | 2688 | declared | support_recall_minus_bad_layers_and_cost | alternating_heads:per_layer_score; early_noise_then_consensus:per_layer_score; late_divergence:per_layer_score; stable_layers:consensus_shared |
| forecast_sparse_routing | 18900 | declared | mass_recall | alternating_heads/B16:oracle_next_layer; alternating_heads/B24:oracle_next_layer; alternating_heads/B8:oracle_next_layer; late_divergence/B16:oracle_next_layer; late_divergence/B24:oracle_next_layer… |
| latent_context_compression | 400 | declared | output_rel_error | adversarial_summary:full_raw_oracle; aligned_chunks:full_raw_oracle; diffuse_target:full_raw_oracle; late_needle:full_raw_oracle; multi_fact_bridge:full_raw_oracle |
| observability_safe_retention | 840 | declared | score | aligned/B16:offline_oracle; aligned/B32:offline_oracle; aligned/B8:offline_oracle; dormant_future/B16:offline_oracle; dormant_future/B32:offline_oracle… |
| evidence_aligned_ttt | 2160 | declared | answer_accuracy | clean_retrieval/K16/S1:oracle_evidence_ttt; clean_retrieval/K16/S3:ease_ttt_softmix; clean_retrieval/K16/S6:oracle_evidence_ttt; clean_retrieval/K4/S1:oracle_evidence_ttt; clean_retrieval/K4/S3:ease_ttt_softmix… |
| parametric_kv_memory | 3000 | declared | rouge_l_proxy | aggressive_compression/base_encoded_answer_only:full_cache_oracle; aggressive_compression/noisy_conflicting:full_cache_oracle; aggressive_compression/none:full_cache_oracle; aggressive_compression/qa_supervised:full_cache_oracle; aggressive_compression/raw_ntp_weak:full_cache_oracle… |
| smt_transition_training | 900 | declared | query_accuracy | bursty_overwrites/B12:ridge_supervised_update; bursty_overwrites/B32:ridge_supervised_update; bursty_overwrites/B4:ridge_supervised_update; long_delays/B12:ridge_supervised_update; long_delays/B32:ridge_supervised_update… |
| still_compactor | 4500 | declared | reconstruction_error | clustered_topics/S16/critical:full_attention; clustered_topics/S16/topic:full_attention; clustered_topics/S32/critical:full_attention; clustered_topics/S32/topic:full_attention; clustered_topics/S8/critical:full_attention… |
| agentic_dfs_search | 2800 | declared | efficiency | deceptive_prefix/D2:oracle_path; deceptive_prefix/D3:oracle_path; deceptive_prefix/D4:oracle_path; deceptive_prefix/D5:oracle_path; deep_generalization/D2:oracle_path… |
| entropy_guided_budget | 1620 | declared | weighted_utility | dynamic_shift/B16:oracle_dynamic; dynamic_shift/B32:oracle_dynamic; dynamic_shift/B64:oracle_dynamic; entropy_trap/B16:oracle_dynamic; entropy_trap/B32:oracle_dynamic… |
| reasoning_cache_share_exit | 1890 | declared | utility | clean_clusters/T0.72:oracle_cluster_exit; clean_clusters/T0.82:oracle_cluster_exit; clean_clusters/T0.90:oracle_cluster_exit; confidence_trap/T0.72:oracle_cluster_exit; confidence_trap/T0.82:oracle_cluster_exit… |
| centaur_hpo_state_smoke | 20 | declared | mean_best_score |  |
| clp_multitoken_acceptance_smoke | 16 | declared | speed_quality_utility |  |
| express_streaming_coreset_cpp_smoke | 64 | declared | mean_mse_to_full_attention |  |
| trace_prefix_rollout_smoke | 48 | declared | mean_reward_contrast |  |
| centaur_hpo_state_smoke | 20 | declared | mean_best_score |  |
| clp_multitoken_acceptance_smoke | 16 | declared | speed_quality_utility |  |
| express_streaming_coreset_cpp_smoke | 64 | declared | mean_mse_to_full_attention |  |
| gated_delta_memory | 15 | declared | mean_retrieval_rel_error |  |
| kvcat_compressibility | 192 | declared | score |  |
| lrkv_head_diversity | 35 | declared | score |  |
| native_token_precision_frontier | 105 | declared | mean_output_rel_error |  |
| query_move_cache_cost | 864 | declared | estimated_us |  |
| query_move_phase_boundary | 4608 | declared | latency_us |  |
| native_residual_kv_sensitivity | 300 | declared | score |  |
| residual_stream_kv | 108 | declared | state_mb |  |
| trace_prefix_rollout_smoke | 48 | declared | mean_reward_contrast |  |
| express_streaming_coreset_cpp_smoke | 64 | declared | mean_mse_to_full_attention |  |
| gated_delta_memory | 15 | declared | mean_retrieval_rel_error |  |
| kvcat_compressibility | 192 | declared | score |  |
| lrkv_head_diversity | 35 | declared | score |  |
| native_token_precision_frontier | 105 | declared | mean_output_rel_error |  |
| query_move_cache_cost | 864 | declared | estimated_us |  |
| query_move_phase_boundary | 4608 | declared | latency_us |  |
| native_residual_kv_sensitivity | 300 | declared | score |  |
| residual_stream_kv | 108 | declared | state_mb |  |
| stochastic_sparse_attention | 240 | declared | score |  |
| dfssm_quant_scaffold | 28 | declared | mean_rel_state_error |  |
| express_streaming_coreset_cpp_smoke | 64 | declared | mean_mse_to_full_attention |  |
| gated_delta_memory | 15 | declared | mean_retrieval_rel_error |  |
| hypergraph_memory_trace | 120 | declared | success_rate |  |
| kvcat_compressibility | 192 | declared | score |  |
| lrkv_head_diversity | 35 | declared | score |  |
| memory_sycophancy_trap | 96 | declared | sycophancy_rate |  |
| native_hpo_phase | 80 | declared | mean_regret_to_dense_grid_optimum |  |
| native_token_precision_frontier | 105 | declared | mean_output_rel_error |  |
| query_move_cache_cost | 864 | declared | estimated_us |  |
| query_move_phase_boundary | 4608 | declared | latency_us |  |
| native_residual_kv_sensitivity | 300 | declared | score |  |
| residual_stream_kv | 108 | declared | state_mb |  |
| stochastic_sparse_attention | 240 | declared | score |  |
| dfssm_quant_scaffold | 28 | declared | mean_rel_state_error |  |
| express_streaming_coreset_cpp_smoke | 64 | declared | mean_mse_to_full_attention |  |
| gated_delta_memory | 15 | declared | mean_retrieval_rel_error |  |
| hypergraph_memory_trace | 120 | declared | success_rate |  |
| kvcat_compressibility | 192 | declared | score |  |
| lrkv_head_diversity | 35 | declared | score |  |
| memory_provenance_phase | 336 | declared | mean_utility |  |
| memory_sycophancy_trap | 96 | declared | sycophancy_rate |  |
| native_hpo_phase | 80 | declared | mean_regret_to_dense_grid_optimum |  |
| native_token_precision_frontier | 105 | declared | mean_output_rel_error |  |
| periodic_cache_rewrite | 25 | declared | mean_utility |  |
| query_move_cache_cost | 864 | declared | estimated_us |  |
| query_move_phase_boundary | 4608 | declared | latency_us |  |
| native_residual_kv_sensitivity | 300 | declared | score |  |
| residual_stream_kv | 108 | declared | state_mb |  |
| stochastic_sparse_attention | 240 | declared | score |  |
| dfssm_quant_scaffold | 28 | declared | mean_rel_state_error |  |
| express_streaming_coreset_cpp_smoke | 64 | declared | mean_mse_to_full_attention |  |
| gated_delta_memory | 15 | declared | mean_retrieval_rel_error |  |
| hypergraph_memory_trace | 120 | declared | success_rate |  |
| native_token_precision_frontier | 105 | declared | mean_output_rel_error |  |
| dfssm_quant_scaffold | 28 | declared | mean_rel_state_error |  |
| express_streaming_coreset_cpp_smoke | 64 | declared | mean_mse_to_full_attention |  |
| gated_delta_memory | 15 | declared | mean_retrieval_rel_error |  |
| hypergraph_memory_trace | 120 | declared | success_rate |  |
| kvcat_compressibility | 192 | declared | score |  |
| lrkv_head_diversity | 35 | declared | score |  |
| memory_provenance_phase | 336 | declared | mean_utility |  |
| memory_sycophancy_trap | 96 | declared | sycophancy_rate |  |
| native_hpo_phase | 80 | declared | mean_regret_to_dense_grid_optimum |  |
| native_residual_kv_sensitivity | 300 | declared | score |  |
| native_token_precision_frontier | 105 | declared | mean_output_rel_error |  |
| vericache_guard | 35 | declared | mean_utility |  |

## Refactor rule

New probes should emit `summary.primary_metric`, a winner map where applicable, and row-level fields with stable metric names. Older probes can be patched gradually rather than rewritten.

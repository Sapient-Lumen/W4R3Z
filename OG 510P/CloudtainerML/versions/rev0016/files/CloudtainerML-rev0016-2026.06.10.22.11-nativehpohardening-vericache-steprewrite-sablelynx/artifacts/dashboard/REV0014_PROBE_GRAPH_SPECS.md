# Probe graph specs — rev0014

This is a plotting plan, not a leaderboard.

| family | probe | metric | chart | facets |
|---|---|---|---|---|
| quantization | kv_wind_tunnel | relative_error | line_or_heatmap |  |
| state-memory | spectral_assoc_recall | accuracy | bar_by_method |  |
| retention | dormant_sponsorship | target_value_retention | line_or_heatmap | budget,policy |
| retention | region_wipeout_cache | coverage_success | line_or_heatmap | budget,policy |
| retention | value_outlier_eviction | critical_value_retention | line_or_heatmap | budget,policy |
| projection | depth_value_mixing | mean_error | bar_by_method | method |
| state-memory | dynamic_state_merging | transition_preservation | line_or_heatmap | policy |
| projection | entmax_support_recovery | output_error | bar_by_method |  |
| retention | moment_directional_gap | reconstruction_error | line_or_heatmap | budget,policy |
| projection | qkv_projection_sharing | relative_error | bar_by_method | regime,variant |
| projection | qkv_projection_sharing | relative_error | bar_by_method |  |
| compaction | tensor_cache_l1_l2 | retrieval_error | bar_by_method |  |
| latent-compute | attention_runtime_termination | relative_error | bar_by_method |  |
| projection | bank_of_values | prediction_accuracy | bar_by_method |  |
| compaction | blurry_window_attention | reconstruction_error | bar_by_method |  |
| routing | branch_cache_sharing | state_match | bar_by_method |  |
| compaction | hierarchical_fademem_cache | reconstruction_error | line_or_heatmap | regime |
| projection | qk_restore_amnesia | recall_accuracy | bar_by_method | regime,method |
| latent-compute | reasoning_wave_budget | retained_mass | bar_by_method | policy |
| quantization | token_precision_frontier | quality_score | bar_by_method | scenario,policy |
| projection | hist_window_order | outgoing_accuracy | line_or_heatmap | regime,method |
| retention | intent_kv_pruning | critical_retention_purity_minus_stale_error | line_or_heatmap | budget,policy |
| latent-compute | latent_reasoning_router | utility | line_or_heatmap | regime,budget,policy |
| routing | pcaf_sparse_memory | mean_exact_success_minus_error_cost | line_or_heatmap | budget |
| routing | shared_routing_once | support_recall_minus_bad_layers_and_cost | line_or_heatmap | budget |
| routing | forecast_sparse_routing | mass_recall | line_or_heatmap | regime,budget,policy |
| compaction | latent_context_compression | output_rel_error | bar_by_method |  |
| retention | observability_safe_retention | score | line_or_heatmap | budget,policy |
| routing | evidence_aligned_ttt | answer_accuracy | line_or_heatmap | regime,policy |
| state-memory | parametric_kv_memory | rouge_l_proxy | line_or_heatmap | regime,policy |
| state-memory | smt_transition_training | query_accuracy | bar_by_method | regime,buffer,policy |
| compaction | still_compactor | reconstruction_error | line_or_heatmap | regime,slots,method |
| agentic-search | agentic_dfs_search | efficiency | bar_by_method | regime,depth,policy |
| routing | entropy_guided_budget | weighted_utility | line_or_heatmap | regime,budget,policy |
| routing | reasoning_cache_share_exit | utility | bar_by_method | regime,policy |
| meta-optimization | centaur_hpo_state_smoke | mean_best_score | bar_by_method | landscape,method |
| decoding-acceleration | clp_multitoken_acceptance_smoke | speed_quality_utility | bar_by_method | regime,policy |
| streaming-coreset | express_streaming_coreset_cpp_smoke | mean_mse_to_full_attention | line_or_heatmap | regime,budget,policy |
| agentic-budget | trace_prefix_rollout_smoke | mean_reward_contrast | line_or_heatmap | regime,budget,policy |
| meta-optimization | centaur_hpo_state_smoke | mean_best_score | bar_by_method | landscape,method |
| decoding-acceleration | clp_multitoken_acceptance_smoke | speed_quality_utility | bar_by_method | regime,policy |
| streaming-coreset | express_streaming_coreset_cpp_smoke | mean_mse_to_full_attention | line_or_heatmap | regime,budget,policy |
| misc | gated_delta_memory | mean_retrieval_rel_error | bar_by_method | regime,policy |
| quantization | kvcat_compressibility | score | bar_by_method |  |
| projection | lrkv_head_diversity | score | bar_by_method | regime,method |
| quantization | native_token_precision_frontier | mean_output_rel_error | bar_by_method | scenario,policy |
| routing | query_move_cache_cost | estimated_us | bar_by_method | policy |
| routing | query_move_phase_boundary | latency_us | bar_by_method | policy |
| state-memory | native_residual_kv_sensitivity | score | bar_by_method | regime,policy |
| state-memory | residual_stream_kv | state_mb | bar_by_method | policy |
| agentic-budget | trace_prefix_rollout_smoke | mean_reward_contrast | line_or_heatmap | regime,budget,policy |
| streaming-coreset | express_streaming_coreset_cpp_smoke | mean_mse_to_full_attention | line_or_heatmap | regime,budget,policy |
| misc | gated_delta_memory | mean_retrieval_rel_error | bar_by_method | regime,policy |
| quantization | kvcat_compressibility | score | bar_by_method |  |
| projection | lrkv_head_diversity | score | bar_by_method | regime,method |
| quantization | native_token_precision_frontier | mean_output_rel_error | bar_by_method | scenario,policy |
| routing | query_move_cache_cost | estimated_us | bar_by_method | policy |
| routing | query_move_phase_boundary | latency_us | bar_by_method | policy |
| state-memory | native_residual_kv_sensitivity | score | bar_by_method | regime,policy |
| state-memory | residual_stream_kv | state_mb | bar_by_method | policy |
| misc | stochastic_sparse_attention | score | bar_by_method | regime |

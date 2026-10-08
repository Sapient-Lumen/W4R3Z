# Probe suite dashboard — rev0014

Artifacts scanned: **61**

| probe | rows | highlight | value | note |
|---|---:|---|---:|---|
| kv_wind_tunnel | 78 | unread |  | no shared metric extracted |
| spectral_assoc_recall | 168 | unread |  | no shared metric extracted |
| dormant_sponsorship | 320 | unread |  | no shared metric extracted |
| region_wipeout_cache | 240 | unread |  | no shared metric extracted |
| value_outlier_eviction | 216 | unread |  | no shared metric extracted |
| depth_value_mixing | 240 | unread |  | no shared metric extracted |
| dynamic_state_merging | 160 | unread |  | no shared metric extracted |
| entmax_support_recovery | 2016 | unread |  | no shared metric extracted |
| moment_directional_gap | 2880 | unread |  | no shared metric extracted |
| qkv_projection_sharing | 750 | qk_aligned_but_v_distinct/share_qk_fit | 0.0195362 | best by mean_output_rel_error |
| qkv_projection_sharing |  | unread |  | no shared metric extracted |
| tensor_cache_l1_l2 | 1536 | unread |  | no shared metric extracted |
| attention_runtime_termination | 1152 | front_loaded/sequential | 0.512153 | lowest read fraction with cosine>=0.99 |
| bank_of_values | 2400 | identity:bank_value_only / context:hybrid_75_bank |  | declared winners |
| blurry_window_attention | 880 | periodic_fact/fft_blurry_32 | 0.00242939 | best by mean_output_l2_error_vs_full |
| branch_cache_sharing | 336 | mild_drift/cosine_0.90 | 0.993056 | lowest cache fraction with unacceptable_error<=0.05 |
| hierarchical_fademem_cache | 1260 | coarse_global/B64->fademem_power | 0.00127211 | best by mean_output_rel_error |
| qk_restore_amnesia | 80 | clean_recall/pre_sft_qk | 0 | best by mean_output_rel_error |
| reasoning_wave_budget | 80 | unread |  | no shared metric extracted |
| token_precision_frontier | 80 | mixed_salience_8_4_2 | 0.351118 | fallback row mean output_rel_error |
| hist_window_order | 1440 | unread |  | no shared metric extracted |
| intent_kv_pruning | 3072 | unread |  | no shared metric extracted |
| latent_reasoning_router | 4608 | unread |  | no shared metric extracted |
| pcaf_sparse_memory | 5376 | unread |  | no shared metric extracted |
| shared_routing_once | 2688 | unread |  | no shared metric extracted |
| forecast_sparse_routing | 18900 | unread |  | no shared metric extracted |
| latent_context_compression | 400 | full_raw_oracle | 0 | fallback row mean output_rel_error |
| observability_safe_retention | 840 | unread |  | no shared metric extracted |
| evidence_aligned_ttt | 2160 | unread |  | no shared metric extracted |
| parametric_kv_memory | 3000 | unread |  | no shared metric extracted |
| smt_transition_training | 900 | unread |  | no shared metric extracted |
| still_compactor | 4500 | unread |  | no shared metric extracted |
| agentic_dfs_search | 2800 | unread |  | no shared metric extracted |
| entropy_guided_budget | 1620 | unread |  | no shared metric extracted |
| reasoning_cache_share_exit | 1890 | unread |  | no shared metric extracted |
| centaur_hpo_state_smoke | 20 | unread |  | no shared metric extracted |
| clp_multitoken_acceptance_smoke | 16 | unread |  | no shared metric extracted |
| express_streaming_coreset_cpp_smoke | 64 | unread |  | no shared metric extracted |
| trace_prefix_rollout_smoke | 48 | unread |  | no shared metric extracted |
| centaur_hpo_state_smoke | 20 | unread |  | no shared metric extracted |
| clp_multitoken_acceptance_smoke | 16 | unread |  | no shared metric extracted |
| express_streaming_coreset_cpp_smoke | 64 | unread |  | no shared metric extracted |
| gated_delta_memory | 15 | unread |  | no shared metric extracted |
| kvcat_compressibility | 192 | unread |  | no shared metric extracted |
| lrkv_head_diversity | 35 | unread |  | no shared metric extracted |
| native_token_precision_frontier | 105 | unread |  | no shared metric extracted |
| query_move_cache_cost | 864 | unread |  | no shared metric extracted |
| query_move_phase_boundary | 4608 | unread |  | no shared metric extracted |
| native_residual_kv_sensitivity | 300 | unread |  | no shared metric extracted |
| residual_stream_kv | 108 | unread |  | no shared metric extracted |
| trace_prefix_rollout_smoke | 48 | unread |  | no shared metric extracted |
| express_streaming_coreset_cpp_smoke | 64 | unread |  | no shared metric extracted |
| gated_delta_memory | 15 | unread |  | no shared metric extracted |
| kvcat_compressibility | 192 | unread |  | no shared metric extracted |
| lrkv_head_diversity | 35 | unread |  | no shared metric extracted |
| native_token_precision_frontier | 105 | unread |  | no shared metric extracted |
| query_move_cache_cost | 864 | unread |  | no shared metric extracted |
| query_move_phase_boundary | 4608 | unread |  | no shared metric extracted |
| native_residual_kv_sensitivity | 300 | unread |  | no shared metric extracted |
| residual_stream_kv | 108 | unread |  | no shared metric extracted |
| stochastic_sparse_attention | 240 | unread |  | no shared metric extracted |

## Refactor note

Next schema target: every probe should emit `probe`, `config`, `summary.row_count`, `rows`, and one declared `primary_metric` block so cross-probe ranking does not require heuristics.
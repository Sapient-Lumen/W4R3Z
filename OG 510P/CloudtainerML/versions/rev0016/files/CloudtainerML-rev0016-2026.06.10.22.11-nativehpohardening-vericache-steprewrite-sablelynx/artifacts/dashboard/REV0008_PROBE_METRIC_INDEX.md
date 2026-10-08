# Probe metric index — rev0008

Artifacts: **25**
Metric-ready: **7**
Needs schema patch: **18**

| probe | rows | status | metric | winners / compact result |
|---|---:|---|---|---|
| kv_wind_tunnel | 78 | needs_schema_patch | missing |  |
| spectral_assoc_recall | 168 | needs_schema_patch | missing |  |
| dormant_sponsorship | 320 | needs_schema_patch | missing |  |
| region_wipeout_cache | 240 | needs_schema_patch | missing |  |
| value_outlier_eviction | 216 | needs_schema_patch | missing |  |
| depth_value_mixing | 240 | needs_schema_patch | missing |  |
| dynamic_state_merging | 160 | needs_schema_patch | missing |  |
| entmax_support_recovery | 2016 | needs_schema_patch | missing |  |
| moment_directional_gap | 2880 | needs_schema_patch | missing |  |
| qkv_projection_sharing | 750 | needs_schema_patch | missing |  |
| qkv_projection_sharing | 0 | needs_schema_patch | missing |  |
| tensor_cache_l1_l2 | 1536 | needs_schema_patch | missing |  |
| attention_runtime_termination | 1152 | needs_schema_patch | missing |  |
| bank_of_values | 2400 | needs_schema_patch | missing |  |
| blurry_window_attention | 880 | needs_schema_patch | missing |  |
| branch_cache_sharing | 336 | needs_schema_patch | missing |  |
| hierarchical_fademem_cache | 1260 | best-policy-map | best_policy_by_regime_budget | full_cache:15 |
| qk_restore_amnesia | 80 | winner-map | winners | clean_recall:pre_sft_qk; cot_local_bias:pre_sft_qk; hard_decoy:pre_sft_qk |
| reasoning_wave_budget | 80 | needs_schema_patch | missing |  |
| token_precision_frontier | 80 | needs_schema_patch | missing |  |
| hist_window_order | 1440 | declared | outgoing_accuracy | adversarial_same_hist:delta_exact; bursty_runs:delta_exact; iid_balanced:delta_exact; low_entropy_cycles:delta_exact |
| intent_kv_pruning | 3072 | declared | critical_retention_purity_minus_stale_error | adversarial_recent_noise:oracle_critical; buried_tool_result:oracle_critical; intent_shift:oracle_critical; stable_intent:oracle_critical |
| latent_reasoning_router | 4608 | declared | utility | easy_smooth:all_flow_latent; hard_spikes:oracle_router; late_brittle:oracle_router; uncertain_but_latent_good:all_latent |
| pcaf_sparse_memory | 5376 | declared | mean_exact_success_minus_error_cost | clean_old_successor:semantic_topk_oracle; noisy_bucket_collision:semantic_topk_oracle; rare_old_fact_vs_recent_noise:semantic_topk_oracle; recurring_entity_update:semantic_topk_oracle |
| shared_routing_once | 2688 | declared | support_recall_minus_bad_layers_and_cost | alternating_heads:per_layer_score; early_noise_then_consensus:per_layer_score; late_divergence:per_layer_score; stable_layers:consensus_shared |

## Refactor rule

New probes should emit `summary.primary_metric`, a winner map where applicable, and row-level fields with stable metric names. Older probes can be patched gradually rather than rewritten.

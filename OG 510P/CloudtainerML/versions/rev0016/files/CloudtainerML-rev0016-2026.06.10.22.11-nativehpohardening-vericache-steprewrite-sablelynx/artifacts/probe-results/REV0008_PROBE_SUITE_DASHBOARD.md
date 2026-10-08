# Probe suite dashboard — rev0008

Artifacts scanned: **25**

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

## Refactor note

Next schema target: every probe should emit `probe`, `config`, `summary.row_count`, `rows`, and one declared `primary_metric` block so cross-probe ranking does not require heuristics.
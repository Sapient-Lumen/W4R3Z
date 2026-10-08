# Evidence integrity audit — rev0068

**Status: boundary_refined_selector_measured_promotion_blocked**

rev0068 repairs the coarse histogram support-width inefficiency with boundary-bin refinement. The repair is scientifically useful but non-promotional because it still computes all QK scores and is slower than dense on this native CPU replay.

## Blockers
- actual_public_pretrained_trace_bundle_missing
- gpu_fused_attention_kernel_timing_missing
- all_deployable_selectors_still_compute_full_qk_scores
- row_local_score_storage_or_prob_storage_still_required
- boundary_refinement_overhead_not_a_fused_kernel_win
- no_deployable_score_path_sparse_win_measured

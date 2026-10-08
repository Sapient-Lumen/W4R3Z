# Evidence integrity audit — rev0066

**Status: support_reuse_amortization_measured_promotion_blocked**

rev0066 directly tests support reuse amortization. Fast anchor reuse is invalid because quality collapses; quality-repairing union support becomes near-dense.

## Blockers
- actual_public_pretrained_trace_bundle_missing
- gpu_fused_attention_kernel_timing_missing
- support_reuse_anchor_quality_below_bar
- support_union_restores_quality_by_becoming_near_dense
- row_stability_certificate_missing
- no_deployable_score_path_sparse_win_measured

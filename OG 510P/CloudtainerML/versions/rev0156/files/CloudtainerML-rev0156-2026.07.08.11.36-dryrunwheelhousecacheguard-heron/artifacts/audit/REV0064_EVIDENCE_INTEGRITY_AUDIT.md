# Evidence integrity audit — rev0064

**Status: value_layout_envelope_measured_promotion_blocked**

rev0064 adds a native CPU value-layout envelope using oracle exact-Top-p support. It corrects a possible mask-scan artifact in rev0063 while preserving all claim blockers around deployability, public/pretrained traces, and GPU/fused timing.

## Blockers
- actual_public_pretrained_trace_bundle_missing
- gpu_fused_attention_kernel_timing_missing
- oracle_topp96_support_is_not_deployable_selector
- packed_value_layout_is_oracle_side_input
- packed_layout_build_cost_not_paid_by_single_query_path
- qk_included_sparse_paths_still_compute_all_qk_scores

## Warnings
- oracle packed-layout envelope shows headroom, but this is not deployable selector/layout evidence

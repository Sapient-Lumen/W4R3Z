# Evidence integrity audit — rev0063

**Status: speed_envelope_measured_promotion_blocked**

rev0063 adds a native CPU speed envelope using oracle exact-Top-p support. It bounds possible selector upside while preserving all claim blockers around deployability, public/pretrained traces, and GPU/fused timing.

## Blockers
- actual_public_pretrained_trace_bundle_missing
- gpu_fused_attention_kernel_timing_missing
- oracle_topp96_mask_is_not_deployable_selector
- materialized_sparse_paths_still_compute_all_qk_scores
- strict_materialization_free_sparse_schedule_has_no_measured_speed_win

## Warnings
- oracle/free-selector envelope shows headroom, but this is not deployable selector evidence

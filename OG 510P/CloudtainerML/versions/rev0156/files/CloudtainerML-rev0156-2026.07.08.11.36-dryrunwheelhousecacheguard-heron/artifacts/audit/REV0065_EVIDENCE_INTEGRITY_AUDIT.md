# Evidence integrity audit — rev0065

**Status: deployable_selector_layout_overhead_measured_promotion_blocked**

rev0065 closes the oracle-layout loophole by paying non-oracle score-only selector and layout construction in native replay. It is accurate but non-promotional because all QK dots remain dense and local CPU paths are slower than dense.

## Blockers
- actual_public_pretrained_trace_bundle_missing
- gpu_fused_attention_kernel_timing_missing
- all_deployable_selector_layout_paths_still_compute_all_qk_scores
- materialized_or_row_local_score_prob_storage_required_for_selector
- no_score_path_sparse_win_measured
- fused_kernel_layout_generation_not_measured

## Warnings
- non-oracle selector/layout construction consumes rev0064 oracle headroom

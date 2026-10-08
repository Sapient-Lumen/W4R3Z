# Current scientific run audit — rev0064

**Status: pass**

rev0064 is a fresh native value-layout envelope replay: it shows whether rev0063 sparse value slowness was a mask-scan/layout artifact while preserving all oracle, public/pretrained, and GPU/fused blockers.

## Current metrics
- trace_packet_rows: `128`
- qk_score_computation_measured_for_qk_included_paths: `True`
- oracle_support_upper_bound_measured: `True`
- oracle_topp96_quality_rate: `1`
- oracle_topp96_mean_selected_fraction: `0.4327392578125`
- mask_scan_value_only_speedup_vs_dense_value_only: `0.691602566537`
- sorted_gather_value_only_speedup_vs_dense_value_only: `1.49717733088`
- packed_value_only_speedup_vs_dense_value_only: `1.59577693342`
- oracle_topp96_qk_included_packed_speedup_vs_dense: `1.148158668`
- packed_layout_build_equivalent_replays: `0.9735835539775916`

## Warnings
- layout matters strongly: mask-scan sparse is slower while selected/packed sparse is faster
- current run shows oracle packed-layout headroom; this is not deployable selector/layout evidence

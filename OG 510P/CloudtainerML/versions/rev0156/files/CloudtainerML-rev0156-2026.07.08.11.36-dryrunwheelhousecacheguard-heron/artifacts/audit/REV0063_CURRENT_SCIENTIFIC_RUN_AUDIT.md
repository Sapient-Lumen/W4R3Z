# Current scientific run audit — rev0063

**Status: pass**

rev0063 is a fresh native speed-envelope replay: it supplies exact Top-p support as an oracle upper bound to test whether selector optimization has measured headroom, while keeping the result non-promotional.

## Current metrics
- trace_packet_rows: `128`
- qk_score_computation_measured: `True`
- oracle_selector_upper_bound_measured: `True`
- oracle_topp96_quality_rate: `1`
- oracle_topp96_mean_selected_fraction: `0.4327392578125`
- oracle_topp96_qk_included_speedup_vs_dense: `1.17350057689`
- oracle_topp96_value_only_speedup_vs_dense_value_only: `0.69679373458`

## Warnings
- current run shows oracle/free-selector headroom; this is not deployable selector evidence

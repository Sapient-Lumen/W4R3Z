# Current scientific run audit — rev0065

**Status: pass**

rev0065 is a fresh native non-oracle selector-layout replay: support and selected layout are built from Q/K scores inside the timed loop, showing whether rev0064 oracle layout headroom survives paid construction.

## Current metrics
- trace_packet_rows: `128`
- selector_layout_overhead_paid_in_timed_loop: `True`
- selectors_use_values_or_dense_outputs: `False`
- qk_dot_fraction_deployable_sparse: `1.0`
- qk_only_fraction_of_dense_time: `0.9278505297869294`
- hist_index_quality_rate: `1`
- hist_index_mean_selected_fraction: `0.66064453125`
- hist_index_speedup_vs_dense: `0.7848788496717704`
- hist_packed_speedup_vs_dense: `0.6476716638007435`
- exact_sort_index_speedup_vs_dense: `0.3497324738523737`
- best_deployable_speedup_vs_dense: `0.7848788496717704`

## Warnings
- fresh non-oracle selector/layout path is slower than dense; rev0064 oracle layout headroom did not survive paid construction
- exact-sort support selects fewer values but costs more than histogram selection

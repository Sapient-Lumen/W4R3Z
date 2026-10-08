# Deployable selector-layout audit — rev0065

**Status: pass**

rev0065 pays score-only selector and selected-layout construction inside native replay. It tests whether rev0064 value-layout headroom survives without oracle support/packed side inputs while preserving all public/pretrained, GPU/fused, and score-path blockers.

## Key metrics
- hist_index_speedup_vs_dense: `0.7848788496717704`
- hist_index_quality_rate: `1`
- hist_index_mean_selected_fraction: `0.66064453125`
- hist_packed_speedup_vs_dense: `0.6476716638007435`
- exact_sort_index_speedup_vs_dense: `0.3497324738523737`
- qk_only_fraction_of_dense_time: `0.9278505297869294`
- best_deployable_speedup_vs_dense: `0.7848788496717704`

## Warnings
- histogram index path is slower than dense once selector/index construction is paid
- per-query packed layout is slower than selected-index gather; rev0064 packed headroom required supplied/reused layout
- exact-sort Top-p selector is much more expensive than histogram selection despite selecting fewer values

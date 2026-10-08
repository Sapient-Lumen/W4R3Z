# Boundary-refined selector audit — rev0068

**Status: pass**

Boundary-bin refinement fixes the coarse histogram over-selection and is cheaper than exact full sort, but it is still slower than dense on this CPU trace and remains blocked because every deployable path computes all QK scores and stores row-local probabilities.

## Key metrics
- `coarse_hist_mean_selected_fraction`: 0.66064453125
- `refined_hist_mean_selected_fraction`: 0.432739257812
- `exact_sort_mean_selected_fraction`: 0.432739257812
- `coarse_minus_exact_mean_selected_count`: 14.5859375
- `refined_minus_exact_mean_selected_count`: 0.0
- `refined_hist_speedup_vs_dense`: 0.4129445432966916
- `exact_sort_speedup_vs_dense`: 0.3460181559024957
- `qk_only_fraction_of_dense`: 0.91967822204

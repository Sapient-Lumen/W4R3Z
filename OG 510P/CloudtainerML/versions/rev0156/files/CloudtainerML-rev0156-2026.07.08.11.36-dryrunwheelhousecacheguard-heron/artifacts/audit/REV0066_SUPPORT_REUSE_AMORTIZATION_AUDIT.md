# Support reuse amortization audit — rev0066

**Status: pass**

rev0066 tests whether support reuse can amortize selector/layout overhead. Anchor reuse saves QK work but fails quality; union support restores quality only by becoming near-dense, so reuse remains non-promotional.

## Key metrics
- fresh_hist_quality_rate: `1`
- fresh_hist_speedup_vs_dense: `0.620788797431`
- reuse_example_anchor_quality_rate: `0.71875`
- reuse_example_anchor_qk_dot_fraction: `0.720581054688`
- reuse_example_anchor_speedup_vs_dense: `1.22871723719`
- reuse_example_anchor_jaccard_mean: `0.465995080527`
- reuse_example_head_anchor_quality_rate: `0.7890625`
- union_example_hist_quality_rate: `1`
- union_example_hist_mean_selected_fraction: `1`

## Warnings
- example-anchor reuse is faster but invalid because quality fails
- union support restores quality only with near-dense/slower support

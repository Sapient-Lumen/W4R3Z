# rev0066 trace-packet support reuse amortization

rev0065 showed that score-only selectors can preserve quality but lose their speed headroom once selector and selected-layout construction are paid per row.  rev0066 tests the next loophole: reuse the selected support across related rows so the selector/layout cost and many QK dots are amortized.

The benchmark uses the local tiny-trained Q/K/V trace packet. It is explicitly **not** public/pretrained evidence and **not** GPU/fused-kernel timing.

Paths:

- dense QK online attention.
- fresh per-row histogram support.
- anchor support reused across rows with the same example.
- anchor support reused across rows with the same example/head.
- an all-row union support upper bound, marked non-promotional because it uses every row in the group to build support and usually becomes near-dense.

The important claim boundary is that support reuse can only be promoted if it preserves output quality while actually reducing score work. Anchor reuse saves QK work but misses row-specific mass; union support restores quality by giving away the sparse win.

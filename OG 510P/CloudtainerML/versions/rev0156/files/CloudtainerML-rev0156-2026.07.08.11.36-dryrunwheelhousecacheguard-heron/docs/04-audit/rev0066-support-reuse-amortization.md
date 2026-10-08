# rev0066 support reuse amortization audit

## Question

Could the rev0065 selector/layout overhead be recovered by reusing support sets across related rows, so that only one anchor row pays the full selector cost and non-anchor rows score only the selected keys?

## Result

No deployable support-reuse path promoted.

- Fresh per-row histogram preserves quality but remains slower than dense on the local CPU trace.
- Example-anchor reuse cuts score work and can look faster, but quality collapses below the output bar.
- Example/head anchor reuse is somewhat more stable, but still below quality bar and not clearly faster.
- All-row union support restores quality only by becoming near-dense, and is marked as a non-promotional upper bound because it uses all rows in the group to construct support.

## Interpretation

Support reuse is not free. It needs a row-stability certificate, not just a cached support list. The local tiny trace shows supports drift enough that anchor reuse misses row-specific attention mass. The repair path is not another selector registry entry; it is either a stronger observable stability certificate, public/pretrained traces showing stable supports, or abandoning this lane for mechanisms that reduce QK work directly.

## Claim boundary

This is local native CPU replay over the tiny-trained Q/K/V packet. It is not public/pretrained evidence, not GPU/fused timing, and not a deployment speedup. Union support is explicitly non-promotional.

# Trace packet QK native replay audit — rev0062

**Status: pass**

rev0062 measures QK score construction inside the native CPU trace replay. The materialized histogram path remains slower than dense and requires global score storage; the no-score-storage streaming path pays a large QK recompute tax.

## Key metrics
- materialized QK speedup vs dense: `0.784128853437`
- streaming recompute speedup vs dense: `0.27619292152`
- quality rate: `0.9921875`
- selected fraction: `0.447875976562`

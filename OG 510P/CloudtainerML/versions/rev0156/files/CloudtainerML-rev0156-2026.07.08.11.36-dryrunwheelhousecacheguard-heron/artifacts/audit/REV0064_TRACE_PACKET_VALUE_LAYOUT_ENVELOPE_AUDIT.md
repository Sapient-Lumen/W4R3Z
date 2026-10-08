# Trace packet value-layout envelope audit — rev0064

**Status: pass**

rev0064 separates mask-scan, selected-index gather, sorted gather, and prepacked selected-value schedules. It can show value-layout headroom, but all exact Top-p support and packed-value paths are oracle/non-deployable upper bounds.

## Key metrics
- mask-scan value-only speedup vs dense value-only: `0.691602566537`
- packed value-only speedup vs dense value-only: `1.59577693342`
- oracle packed QK-included speedup vs dense: `1.148158668`
- quality rate: `1`
- packed layout build equivalent replays: `0.973583553978`

## Warnings
- oracle packed qk-included path clears dense; this is layout headroom, not deployable selector evidence

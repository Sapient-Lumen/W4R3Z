# Trace packet native replay audit — rev0061

**Status: pass**

rev0061 measures the learned trace packet through native materialized-score CPU loops and vetoes proxy-only sparse promotion because the measured histogram score-consumption path is slower than dense on this packet.

## Key metrics
- native speedup vs dense score consumption: `0.810951219572`
- rev0060 proxy speedup: `1.2770849410104002`
- quality rate: `1.0`
- mean selected fraction: `0.45166015625`

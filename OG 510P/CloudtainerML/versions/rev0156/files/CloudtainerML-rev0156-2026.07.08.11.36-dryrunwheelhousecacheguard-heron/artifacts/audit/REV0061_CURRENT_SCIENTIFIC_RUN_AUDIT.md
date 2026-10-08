# Current scientific run audit — rev0061

**Status: pass**

- native speedup vs dense score consumption: `0.810951219572`
- rev0060 proxy speedup: `1.2770849410104002`
- quality rate: `1.0`
- qk score computation measured: `False`

Current rev0061 evidence is native CPU materialized-score replay over the learned trace packet. It strengthens the proxy veto: quality survives, but the measured histogram score-consumption path is slower than dense, while QK/public/GPU blockers remain open.

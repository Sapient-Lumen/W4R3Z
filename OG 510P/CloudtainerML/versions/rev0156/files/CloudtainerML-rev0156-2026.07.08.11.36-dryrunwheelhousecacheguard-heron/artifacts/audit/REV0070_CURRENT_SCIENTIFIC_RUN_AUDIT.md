# Current scientific run audit — rev0070

**Status: pass**

rev0070 replaces the full outside-token certificate scan with a two-stage key-cache sidecar. The safety result holds and metadata reads drop, but the safe path remains slower than dense/fresh histogram on local CPU traces.

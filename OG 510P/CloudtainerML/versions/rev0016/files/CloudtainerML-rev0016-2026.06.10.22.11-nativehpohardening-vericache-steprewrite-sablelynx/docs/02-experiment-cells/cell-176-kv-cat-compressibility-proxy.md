# CELL-176: KV-CAT Compressibility Proxy

Priority: P0

Status: runnable

Idea: IDEA-0175

Source: SRC-0123

Cheap first run: experiments/kvcat_compressibility/kvcat_compressibility.cpp emits REV0014_KVCAT_COMPRESSIBILITY_SMOKE.json.

Metrics:
- reconstruction MSE
- retrieval accuracy
- score

Baselines:
- base isotropic
- KV-CAT-like clustered
- uniform thinning
- prototype compression
- needle-aware compression

Stop condition: If geometry does not matter, toy misses core claim.

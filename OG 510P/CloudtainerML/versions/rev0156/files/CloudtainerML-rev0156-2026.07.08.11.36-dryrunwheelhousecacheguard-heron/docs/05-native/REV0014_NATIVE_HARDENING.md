# rev0014 native hardening

C++ is now the preferred implementation for stable high-volume probes. This revision adds five native probes and strengthens native audit hygiene.

| Probe | Path | Output |
|---|---|---|
| Residual/KV sensitivity | `experiments/native_residual_kv_sensitivity/residual_kv_sensitivity.cpp` | `REV0014_RESIDUAL_KV_SENSITIVITY_SMOKE.json` |
| Query move phase scan | `experiments/query_move_phase_boundary/query_move_phase_scan.cpp` | `REV0014_QUERY_MOVE_PHASE_SCAN_SMOKE.json` |
| LRKV head diversity | `experiments/lrkv_head_diversity/lrkv_head_diversity.cpp` | `REV0014_LRKV_HEAD_DIVERSITY_SMOKE.json` |
| Stochastic sparse attention | `experiments/stochastic_sparse_attention/stochastic_sparse_attention.cpp` | `REV0014_STOCHASTIC_SPARSE_ATTENTION_SMOKE.json` |
| KV-CAT compressibility | `experiments/kvcat_compressibility/kvcat_compressibility.cpp` | `REV0014_KVCAT_COMPRESSIBILITY_SMOKE.json` |

Native audit compiles every C++ file in a temporary directory and rejects checked-in binaries.

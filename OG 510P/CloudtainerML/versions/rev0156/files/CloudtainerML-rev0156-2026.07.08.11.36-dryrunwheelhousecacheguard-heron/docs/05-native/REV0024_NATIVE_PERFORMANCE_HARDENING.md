# rev0024 native performance hardening notes

Fresh native probes in this revision:

| Probe | Why it exists |
|---|---|
| `subspace_moe_router` | STAR/MoE-testbed style routing under rare-domain and load traps |
| `oracle_sparse_prefill_gap` | Separates sparse support budget, indexer, and realization errors |
| `tensor_matrix_decomp_sanity` | Prevents elegant tensor compression from skipping matrix baselines |
| `attention_sink_mechanism` | Diagnoses NOP versus broadcast sinks before choosing interventions |
| `real_speed_flops_guard` | Catches FLOP-vs-wall-time reversal in pruning/sparsity screens |

Recommendation: use native HPO on **one** of these before adding another family.

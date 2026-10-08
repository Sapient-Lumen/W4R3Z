# CELL-312 — Expert-Choice Sparse Attention Frontier

Priority: **P0**  
Status: `coded-native-frontier`

## Why it exists

When does MoSA-style head-specific content sparsity beat LoLA-style sparse caching, local windows, and dense attention under equal-cost scoring?

## Cheap first run

Run REV0030_EXPERT_CHOICE_SPARSE_ATTENTION_SMOKE.json; compare MoSA-style expert choice to LoLA-style cache and dense.

## Metrics

- `score`
- `recall`
- `error`
- `cost_frac`
- `head_collision`
- `tail_miss`
- `cache_staleness`
- `regret`

## Required baselines

- `dense_attention`
- `uniform_sparse`
- `cluster_routing`
- `mosa_expert_choice`
- `lola_sparse_cache`
- `hybrid_mosa_lola`

## Stop condition

Do not promote if rare-tail or head-collision fields erase sparse wins.

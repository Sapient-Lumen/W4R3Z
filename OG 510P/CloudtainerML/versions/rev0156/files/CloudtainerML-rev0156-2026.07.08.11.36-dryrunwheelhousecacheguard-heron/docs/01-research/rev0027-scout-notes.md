# Rev0027 scout notes — performance-first hunt

## Strongest new hit: MPI routers

`SRC-0307` proposes aligning MoE router rows with expert principal singular directions via a power-then-retract update. This is unusually testable at tiny scale because we can separate router/expert alignment, load balance, rare-domain miss, and drift without training a large MoE.

## Other useful hits

- `SRC-0308` nD-RoPE suggests a geometry-only probe: axis-separable versus isotropic wave-vector position encodings.
- `SRC-0309` VIA-SD suggests a cost frontier for direct acceptance, slim verification, and full verification.
- `SRC-0310` multi-rate MoE for liquid networks suggests fast/slow expert time constants as a future sequence toy.
- `SRC-0312` / `SRC-0314` sharpen the subquadratic guardrail: do not promote methods only because they solve easy single-needle retrieval.

## Fresh code this turn

- `experiments/manifold_power_router/manifold_power_router.cpp`
- `experiments/starkv_svd_hpo/starkv_svd_hpo.cpp`
- `experiments/via_sd_tiered_verifier/via_sd_tiered_verifier.cpp`
- `experiments/nd_rope_isotropy/nd_rope_isotropy.cpp`
- `experiments/sparse_lowrank_hybrid_frontier/sparse_lowrank_hybrid_frontier.cpp`

## Priority shift

MPI router alignment enters P0. STAR-KV rank HPO stays P0 but is now in hardening mode. Sparse/low-rank hybrid frontiers are promoted because they help arbitrate many older sparse-attention claims under equal-budget tail/wall metrics.

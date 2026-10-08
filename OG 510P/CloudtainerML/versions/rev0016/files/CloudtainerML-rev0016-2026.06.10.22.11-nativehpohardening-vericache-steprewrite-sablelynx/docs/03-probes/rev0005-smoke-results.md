# rev0005 smoke results

Smoke outputs live in `artifacts/probe-results/`. These are cheap falsifiers, not faithful reproductions of the cited papers.

## QKV projection-sharing

Artifact: `REV0005_QKV_PROJECTION_SHARING_SMOKE.json` / `.csv`

The tensor-only probe creates teacher Q/K/V projections under several geometry regimes and least-squares-fits tied variants. In the `aligned_kv` regime, `share_kv_fit` had mean relative output error about `0.072`, output cosine about `0.997`, and cache factor `0.5`. Q=K and all-shared variants collapsed more because symmetric score maps lose directionality.

Interpretation: K=V sharing is worth probing, but the baby benchmark must include regimes where value directions are genuinely independent.

## Moment directional-gap

Artifact: `REV0005_MOMENT_DIRECTIONAL_SMOKE.json` / `.csv`

The constructed setting makes low-mass evicted vectors carry missing directions. Top-attention kept-only policies had large normalized errors at tight budgets, while a first-order moment correction dropped errors to near-zero in the smoke setup.

Interpretation: moment correction is a strong P0 toy because it exposes an error mode that mass-only retention misses.

## Tensor Cache L1/L2

Artifact: `REV0005_TENSOR_CACHE_L2_SMOKE.json` / `.csv`

Sliding-window-only forgot old targets in the smoke setup. L2 per-token outer-product writes recovered old targets; chunk-mean shortcuts collapsed on retrieval, making the spurious-cross-term warning visible in miniature.

Interpretation: Tensor Cache is worth keeping as the most direct associative-memory bridge between full attention and bounded state.

## Entmax support recovery

Artifact: `REV0005_ENTMAX_SUPPORT_SMOKE.json` / `.csv`

Sparse support turns cache selection into support recovery. Random pages failed, page scoring helped, and exact token-top-k was the upper anchor; dropped mass tracked output error.

Interpretation: support coverage may be a cleaner metric than approximate softmax tail retention for sparse-attention cache work.

## Depth-value mixing

Artifact: `REV0005_DEPTH_VALUE_MIXING_SMOKE.json` / `.csv`

The probe creates depth stacks where signal monotonically improves, peaks at mid-depth, is corrupted late, or includes a decoy layer. Final-only is best in monotonic cases but fails badly when the best layer is earlier. Query-conditioned depth mixing and oracle variants are useful upper/lower anchors.

Interpretation: depth can be treated as a small cache axis before building any trained cross-layer model.

## Dynamic state merging

Artifact: `REV0005_DYNAMIC_STATE_MERGING_SMOKE.json` / `.csv`

Under equal state budgets, dynamic drift-aware merging beat fixed/uniform and recency-biased block summaries on transition MSE and boundary F1 in the smoke setup.

Interpretation: this is a good pre-training-stage proxy for dynamic linear-attention claims: first prove boundaries matter, then train.

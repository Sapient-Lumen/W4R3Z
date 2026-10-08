# rev0053 learned-trace block-bound score audit

## Why this revision exists

rev0052 made score-path block pruning honest on synthetic key caches by computing centroids and radii from the key cache rather than from generator-side truth. The remaining risky question was whether those observable block bounds are tight on traces produced by a trained attention layer.

rev0053 trains a tiny retrieval transformer, captures final-query Q/K/V rows, and benchmarks block upper-bound pruning under the same selection contract used by the attention compiler work:

- selectors may use Q and K;
- selectors may build block centroids/radii from K;
- selectors may use score-only mass certificates;
- selectors may not inspect V vectors or dense outputs before selecting indices.

## Substantive result

The tiny model reaches 1.0 eval accuracy, so the traces are learned model traces rather than random-init traces. They are still not public/pretrained evidence.

On aggregate learned rows:

- dense score-mass histogram keeps quality but still computes all QK scores (`qk_dot_fraction_vs_dense = 1.0`);
- PCA-sorted observable blocks reach `quality_bar_rate = 1.0` with aggregate `qk_dot_fraction_vs_dense ≈ 0.944`;
- low-support rows are the only strong score-skip case (`qk_dot_fraction_vs_dense ≈ 0.526`);
- high-support rows erase the advantage (`qk_dot_fraction_vs_dense ≈ 1.141`);
- sampled-radius PCA blocks are explicitly unsafe (`mean_bound_violation_rate ≈ 0.434`).

## Interpretation

This is a useful narrowing result. Score-path block pruning is not broadly promoted. It is conditionally promising when learned attention rows are low-support and key-cache geometry makes observable block radii tight. For higher-support rows, the bound opens nearly everything and can cost more QK dot-equivalents than dense scoring once block bound dots are counted.

The next high-value work is to run the same importer on an actual public/pretrained Q/K/V trace bundle and to implement a fused/kernel-oriented block-bound path. Until then, the cube should not claim deployment speedups.

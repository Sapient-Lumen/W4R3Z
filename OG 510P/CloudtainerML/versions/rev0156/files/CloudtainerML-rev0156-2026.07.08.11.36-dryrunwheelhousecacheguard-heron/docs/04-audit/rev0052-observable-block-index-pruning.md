# rev0052 observable block-index pruning

## Why this revision exists

rev0051 found that block upper-bound pruning can skip exact token QK score computation in tight clustered regimes. The risky part was that the benchmark used generator-side block centroids/radii. That made the result useful as a possibility proof, but too privileged for a deployable claim.

rev0052 removes that privilege. The current candidate computes a block centroid and max radius directly from the key cache, before seeing the query. The benchmark reports query-path timing and index-build cost separately, including 32-query reuse amortization.

## Current finding

Observable key-cache bounds preserve the tight peaked case:

- QK dot fraction around 0.047 of dense.
- Reuse-amortized CPU speedup above dense.
- Quality bar passes.

But the win is narrow:

- Broad unstructured caches collapse to near/full dense QK work.
- Loose clustered caches also collapse to dense work.
- Multipeak tight caches prune some score work but are not a CPU speed win because overhead dominates.

## Negative control

`unsafe_sampled_radius4_block_pruned_0p95_sparse` estimates each block radius from only four tokens. It can look sparse, but the audit detects nonzero upper-bound violations. These rows are intentionally non-promotable.

## Status

Promotion remains blocked until the same observable-index path is tested on public/pretrained Q/K/V traces and implemented in a GPU/fused-kernel setting.

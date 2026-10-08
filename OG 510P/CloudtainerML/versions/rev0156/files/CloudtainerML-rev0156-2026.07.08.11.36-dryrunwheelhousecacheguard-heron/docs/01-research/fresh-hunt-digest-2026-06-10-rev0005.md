# Fresh hunt digest — rev0005

## User-linked paper: QKV projection sharing

Paper `2606.04032` is highly aligned with the cache/memory lane. It asks whether attention really needs three independent Q/K/V projections and reports that the separate-query / shared-key-value variant (`K=V`, paper notation `Q-K=V`) can halve KV cache storage while keeping language-model quality close to full QKV at large scale.

Cloudtainer-scale translation: do not reproduce their large run. Ask which tiny geometries actually need independent value directions.

Runnable fast probe: `experiments/qkv_projection_sharing/qkv_projection_sharing_probe.py`.

Slower draft trained harness: `experiments/qkv_projection_sharing/qkv_projection_probe.py`.

## Cache eviction: directional gap

MomentKV argues that cache eviction can fail because the evicted set is directionally different from the retained set, even when residual attention mass is small. This extends earlier region-wipeout/value-outlier traps: retention should preserve missing vector directions, not only mass.

Runnable probe: `experiments/moment_directional_gap/moment_directional_probe.py`.

## Tensor Cache: L1 exact window + L2 associative memory

Tensor Cache accepts sliding-window eviction, then writes evicted KV pairs into an outer-product memory. The baby test asks whether old facts outside the window can be recovered by a fixed L2 memory and whether chunked-mean shortcuts visibly create spurious cross-token products.

Runnable probe: `experiments/tensor_cache_l2/tensor_cache_probe.py`.

## EntmaxKV: support recovery rather than dense-tail approximation

EntmaxKV reframes sparse decoding around exact support recovery: if selected pages contain the entmax support, output error can vanish. The baby test compares page scoring policies by dropped mass and support coverage.

Runnable probe: `experiments/entmax_support_recovery/entmax_support_probe.py`.

## Depth as a cache axis

Depth-Attention / cross-layer value mixing suggests the model may need access not only to earlier tokens, but also to earlier depth representations. The cheap test is a tensor stack where the best signal can appear at mid-depth or be corrupted late.

Runnable probe: `experiments/depth_value_mixing/depth_value_mixing_probe.py`.

## Dynamic state merging

Dynamic Linear Attention makes fixed state merging look suspect for non-stationary streams. The cheap test is to compare fixed, recency, random, and drift-aware state summaries under the same state budget.

Runnable probe: `experiments/dynamic_state_merging/dynamic_state_merging_probe.py`.

## New non-cache scouting lanes

- Supervised Memory Training: transformer teacher supplies memory-transition labels for recurrent learners.
- Ordinal geometry: local comparisons can induce rank manifolds and symbolic-distance behavior.
- Low-rank KV/head diversity: preserve head function through low-rank residuals instead of full independent KV.
- Spectral denoise-then-quantize: split shared low-rank cache structure from residual before low-bit quantization.
- Circuit discovery as bandit/RL: use interventions as actions rather than hand-written mechanistic pipelines.

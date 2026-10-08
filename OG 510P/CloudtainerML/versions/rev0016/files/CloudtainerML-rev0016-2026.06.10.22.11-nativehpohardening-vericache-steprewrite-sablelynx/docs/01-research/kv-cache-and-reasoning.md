# KV cache and reasoning lane

Core sources: `SRC-0001`, `SRC-0002`, `SRC-0003`, `SRC-0039` through `SRC-0050`.

## Main hypothesis cluster

- Long generated traces make the cache a bottleneck and also a fragile substrate.
- Static/prefill-style tests may miss decode-time accumulation.
- Some tokens, heads, layers, or segments matter disproportionately for final answers.
- A cache can be more than a speedup: it can be a cheap latent state for routing, sampling, or deciding when to think longer.

## Tiny experiments

- Quantize K/V tensors and run pseudo-decode sweeps.
- Train a learned retention gate from an oracle full-cache teacher.
- Label synthetic reasoning traces with exact dependency graphs and test token/segment/head removal.
- Summarize K/V tensors into features and predict correctness or need-more-compute.

## Warning

Do not use sparse retrieval alone as the benchmark. Include high-density dependency traces where every step matters.

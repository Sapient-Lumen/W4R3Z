# Research scout notes — rev0022

## Added / promoted sources

- A3 component-aware low-rank approximation: useful because it splits QK, OV, and MLP functional losses instead of generic low-rank layer error.
- Gated Subspace Inference: useful because it targets linear-layer bandwidth through low-rank activation manifolds plus per-token residual gates.
- Make Each Token Count: useful because it argues selective KV retention can improve performance by reducing attention dilution.
- Exact Linear Attention and Low-Rank Decay were promoted because they are cheap to falsify at tiny scale.

## Current reading pressure

The next hunt should favor papers with a clear equal-budget toy falsifier: rank allocation, gating thresholds, kernel dilution, spectral regularization, search/backtracking mechanisms, or C++ phase boundaries.

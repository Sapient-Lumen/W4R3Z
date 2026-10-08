# rev0023 scout notes — performance-first architecture hunt

This turn keeps CloudtainerML centered on tiny-scale performance/surprise. New papers were selected because they imply cheap tests, not because they are fashionable.

## Promoted sources

- SRC-0273 Dynamic Short Convolutions Improve Transformers: test dynamic local filters as a primitive.
- SRC-0274 Dynamic sparsity in tree-structured FFN layers: test hard conditional MLP sparsity and auto-pruning failure modes.
- SRC-0275 Curvature-Conditioned Query for Linear Attention: test query geometry in fast-weight memories.
- SRC-0276 Adaptive Memory Decay for Log-Linear Attention: test input-dependent hierarchy decay.
- SRC-0277 CART: use its negative screen/full reversal result as a guardrail for CloudtainerML HPO.

## New questions

The turn adds questions around local mixing, rare expert leaves, fast-weight dilution, adaptive decay, and cheap-screen regret. The strongest trained escalation candidates remain learned subspace gates, low-rank-decay modular arithmetic, agentic DFS, and now dynamic-locality or tree-FFN routing if their probes harden.

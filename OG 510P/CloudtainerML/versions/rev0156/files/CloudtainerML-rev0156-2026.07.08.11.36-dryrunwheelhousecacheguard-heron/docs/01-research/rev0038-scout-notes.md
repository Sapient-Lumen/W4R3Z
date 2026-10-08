# rev0038 scout notes — hard bridge compilation

Core focus remains tiny-scale performance and architecture surprise, with security/trust material bounded as a side wing.

## New / reweighted sources

- MiniMax Sparse Attention: blockwise sparse attention on GQA with a lightweight Index Branch, local-block retention, and kernel co-design. The CloudtainerML translation is not large-model training; it is whether block/index compilers preserve exact reachability and cost fields in tiny sparse-program tests.
- Gated Sparse Attention: bounded sigmoid selection scores, adaptive sparsity and value/output gates. This is useful as a future contrast to our current result that raw sigmoid probabilities can be badly calibrated for hard deployment.
- SpargeAttention: training-free two-stage filtering. This becomes a useful baseline for gate compilation: score filters versus post-trained soft gates versus top-k compilers.

## Main interpretation shift

The learned boundary repair result from rev0037 becomes sharper in rev0038: the sparse mechanism is not just the learned gate. It is the full pipeline:

```text
train soft/dense mechanism
→ learn or infer sparse scores
→ compile scores into hard connectivity
→ verify exactness/reachability
→ charge selected-edge/page cost
```

The key new hypothesis: **ranked soft gates can be useful even when their absolute probabilities are useless.**

# rev0039 scout notes — block index, exact top-k, and annealed sparse gates

This revision keeps the center on tiny-scale performance and hard deployability of sparse mechanisms.

## New source pressure

- MiniMax Sparse Attention makes blockwise GQA index branches concrete: a lightweight index branch selects key/value blocks per GQA group, with local-block retention and a main branch that performs exact block-sparse softmax over selected blocks.
- Guess-Verify-Refine makes top-k selection itself a performance object: previous-step top-k can predict current sparse-attention support, but exactness requires verify/refine/fallback.
- SpargeAttention2 and Top-Theta/compensated thresholding keep the gate-compiler question alive: top-k, top-p, threshold, and hybrid compilers fail in different score-row regimes.

## Working interpretation

Sparse attention is becoming a compiler stack rather than one mechanism:

```text
score / gate / index branch
  -> compiler: threshold, top-k, top-p, validation, GVR
  -> selector kernel / block layout
  -> exactness and cost guards
```

The next serious tests should avoid reporting sparse accuracy without selector cost and hard-deployment exactness.

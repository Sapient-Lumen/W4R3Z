# rev0023 native performance extensions

New C++ probes:

- `dynamic_short_convolution.cpp` — dynamic local filters vs static convolution/plain attention.
- `tree_sparse_ffn_autoprune.cpp` — conditional FFN routing, rare leaves, auto-pruning.
- `curvature_query_fastweights.cpp` — query-shaped fast-weight readout under dilution.
- `adaptive_fenwick_decay.cpp` — input-dependent log-level memory decay.
- `cart_screen_reversal.cpp` — cheap screen vs full-training reversal guard.

The strongest code surprise in this revision is not one single winner; it is that the most interesting lanes are conditional. Dynamic convolution wants real locality, tree sparsity wants repair/balance, fast weights want query geometry under bulk distractors, and HPO screens need regret guards.

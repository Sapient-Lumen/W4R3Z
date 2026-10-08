# CELL-055 — Bank-of-Values Identity Preservation Probe

Priority: P0
Status: candidate-with-runnable-probe
Sources: SRC-0106

Question: When do context-free token value banks beat residual-derived values, and when do they erase needed context?

Cheap first run: Synthetic attention lookup with context drift/noise and contextual signal sweeps.

Baselines: context-only values, static value bank, 25/50/75% hybrid bank mixes, oracle target vectors

Metrics: identity cosine, context cosine, identity MSE, context MSE, attention entropy

Stop condition: If bank-only cannot win identity preservation or hybrids cannot win contextual tradeoff, drop.

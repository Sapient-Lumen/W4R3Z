# Fresh hunt digest — rev0004

Posture: still scouting. This revision adds three runnable symbolic probes because the latest hunt keeps converging on cache retention failure modes that can be falsified before training a model.

## New hot leads

- **Latent-memory eviction**: evicted KV tokens are not simply dropped; they can be summarized into an online residual memory. This points toward an L1 exact cache + L2 associative cache experiment.
- **Value-aware stochastic eviction**: value-norm outliers may be causal stabilizers in reasoning traces, and stochastic retention may preserve cache diversity better than deterministic top-k.
- **Tensor Cache**: an outer-product L2 memory fed exclusively by evictions is almost tailor-made for our existing spectral associative recall probe.
- **EntmaxKV / sparse support**: sparse attention creates a different pruning success criterion: recover the support, not approximate dense softmax tails.
- **Attractor/looped reasoning**: fixed-point refinement and compressed-loop-vs-scratchpad questions are increasingly important, but likely need a trained tiny task after the cache probes mature.
- **Weights-to-code / finite-state extraction**: the best success artifact may be an executable recovered program or DFA, not a validation curve.

## What became code

- `experiments/region_wipeout_cache/region_wipeout_probe.py`
- `experiments/dormant_sponsorship/dormant_sponsorship_probe.py`
- `experiments/value_outlier_eviction/value_outlier_probe.py`

## Current bias

Run cheap falsifiers first. If the symbolic probes show robust separations, instrument the same traps inside a tiny transformer.

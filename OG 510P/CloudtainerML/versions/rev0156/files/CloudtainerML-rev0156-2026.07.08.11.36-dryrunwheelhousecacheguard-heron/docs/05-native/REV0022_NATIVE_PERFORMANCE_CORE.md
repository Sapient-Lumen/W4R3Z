# Native performance core — rev0022

This revision adds five C++17 probes. They are source-only and validated through the native audit.

## New probes

1. Component rank allocator — A3-style QK/OV/MLP functional rank budgets.
2. Gated subspace inference — residual correction gates under cost/error tradeoffs.
3. ELA dilution — linear/positive kernels under target-mass dilution.
4. LRD dynamics — spectral regularization proxy for grokking.
5. Attention dilution eviction — full cache versus selective retention under distractors.

## Next native hardening

Add an HPO sweep harness over one of these new probes, or take spectra/features from a tiny trained PyTorch model and feed them into the C++ probes.

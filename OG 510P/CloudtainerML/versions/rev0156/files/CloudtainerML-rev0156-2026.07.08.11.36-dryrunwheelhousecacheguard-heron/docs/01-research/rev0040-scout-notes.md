# Research scout notes — rev0040

## Current external pattern

Recent sparse-attention work reinforces the cube’s choice of mechanism family:

- **MiniMax Sparse Attention** (arXiv:2606.13392) uses a lightweight per-GQA-group block index branch and a co-designed sparse kernel.
- **You Only Index Once / CLSA** (arXiv:2606.06467) amortizes token routing by reusing an index across layers.
- **Guess, Verify, and Refine** (arXiv:2604.22312) uses indexed statistics, candidate counting, verification, and exact refinement rather than a ground-truth membership oracle.
- **SpargeAttention2** (arXiv:2602.13515) combines Top-K and Top-p style sparsity with distillation and kernel work.
- **Top-Theta** (arXiv:2502.08363) explores calibrated thresholding that avoids a full-vector Top-K dependency.

The common lesson is that the selector is only part of the mechanism. Index construction, verification, memory movement, kernel layout, fallback behavior, and model-quality retention are first-class.

## Provenance comparison

Established provenance models separate the artifact/entity, the activity that generated it, and the responsible agent/environment. Reproducible ML tracking systems likewise record parameters, code versions, metrics, timings, and artifacts. Software supply-chain provenance records which builder produced an artifact from which build definition. CloudtainerML should adopt the same shape for scientific runs rather than encoding lineage in filenames.

## Implication for this cube

The research direction is timely, but the local toys should be described as abstractions unless they reproduce the operative algorithm and measured system path. The next work should narrow, not broaden: one canonical task, several compilers, explicit exactness, immutable lineage, and real timing.

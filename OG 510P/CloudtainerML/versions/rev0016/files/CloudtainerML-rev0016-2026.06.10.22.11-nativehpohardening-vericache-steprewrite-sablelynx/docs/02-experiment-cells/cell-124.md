# CELL-124 — Cross-Model State Patch Toy

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0123`  
Sources: SRC-0181

## Cheap first run

Simulate producer/consumer latent mismatch and patch selected semantic regions.

## Metrics

- state transfer error
- patch sparsity
- reuse gain

## Required baselines

- raw reuse
- global affine patch
- selective patch
- recompute oracle

## Stop condition

If global patch solves all regimes, make harder mismatch.

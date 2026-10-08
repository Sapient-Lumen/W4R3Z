# CELL-220 — Linear-Constrained VQ Tiny Quantizer

Priority: **P2**  
Status: **candidate**  
Idea: `IDEA-0219`  
Sources: SRC-0246

## Cheap first run

Tiny matrix quantization with scalar 2-bit, VQ lookup, and linear-constrained VQ.

## Metrics

- MSE
- task loss
- training data needed
- codebook overhead

## Required baselines

- scalar quant
- unconstrained VQ
- linear-constrained VQ
- fp32

## Stop condition

If overhead dominates benefits, keep as paper note.

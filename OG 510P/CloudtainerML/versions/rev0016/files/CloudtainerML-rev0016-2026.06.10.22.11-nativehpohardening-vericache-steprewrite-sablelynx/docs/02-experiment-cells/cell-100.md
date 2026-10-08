# CELL-100 — Express Causal Approximation Matrix Toy

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0100`  
Sources: SRC-0146

## Cheap first run

Causalize non-causal attention approximations on matrix families.

## Baselines

- full causal
- noncausal sketch
- causal sketch
- sliding block
- random

## Metrics

- approx_error
- leakage
- memory
- compression_overhead

## Stop condition

If trivial baselines dominate, park.

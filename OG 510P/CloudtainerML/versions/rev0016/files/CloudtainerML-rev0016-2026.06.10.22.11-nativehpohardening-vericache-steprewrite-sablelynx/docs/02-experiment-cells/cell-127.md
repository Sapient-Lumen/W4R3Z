# CELL-127 — Low-Rank Decay Grokking Probe

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0126`  
Sources: SRC-0184

## Cheap first run

Tiny modular arithmetic with spectral regularization variants.

## Metrics

- test accuracy
- rank proxy
- spectral collapse timing

## Required baselines

- weight decay
- low-rank decay proxy
- no regularizer

## Stop condition

If low-rank decay only underfits, demote.

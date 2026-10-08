# CELL-211 — Latent/Discrete Reasoning Router Revisit

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0211`  
Sources: SRC-0239

## Cheap first run

Test a cheap router for visible versus latent reasoning budget on long narrative/retrieval synthetic tasks.

## Metrics

- accuracy
- visible token count
- latent step count
- utility

## Required baselines

- all visible
- all latent
- router
- oracle router

## Stop condition

If latent steps only behave like a scalar summary, fold into compression lane.

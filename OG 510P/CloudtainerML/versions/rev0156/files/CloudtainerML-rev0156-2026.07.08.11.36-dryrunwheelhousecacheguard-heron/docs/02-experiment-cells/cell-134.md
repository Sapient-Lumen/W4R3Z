# CELL-134 — Latent Compactor Hybridization Sweep

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0133`  
Sources: SRC-0180

## Cheap first run

Sweep needle frequency and latent/top-k budget split.

## Metrics

- critical hit proxy
- cluster error
- budget split

## Required baselines

- all latent
- all top-k
- hybrid split

## Stop condition

If no hybrid region exists, simplify.

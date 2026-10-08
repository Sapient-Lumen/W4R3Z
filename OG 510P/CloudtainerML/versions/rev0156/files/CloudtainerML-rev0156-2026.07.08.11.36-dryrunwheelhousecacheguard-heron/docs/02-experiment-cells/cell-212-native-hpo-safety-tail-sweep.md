# CELL-212 — Native HPO Safety-Tail Sweep

Priority: **P0**  
Status: **candidate_hardening**  
Idea: `IDEA-0212`  
Sources: SRC-0127, SRC-0195

## Cheap first run

Use native HPO phase harness to sweep safety-subspace probe parameters.

## Metrics

- phase transition sharpness
- best mitigation
- search efficiency
- tail divergence

## Required baselines

- grid
- random
- domain prior
- centaur state prior

## Stop condition

If hand grid finds same boundary cheaper, keep HPO for broader phase maps.

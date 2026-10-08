# CELL-096 — Latent Reconstruction Gate

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0096`  
Sources: SRC-0159, SRC-0158

## Cheap first run

Use reconstruction error to verify latent state before passing forward.

## Baselines

- no check
- reconstruct next state
- reconstruct explicit trace
- oracle

## Metrics

- correlation_with_success
- repair_rate
- false confidence

## Stop condition

If reconstruction not predictive, drop.

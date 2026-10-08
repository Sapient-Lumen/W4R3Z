# CELL-095 — Latent/Explicit Reasoning Router Toy

Priority: **P0**  
Status: **runnable**  
Idea: `IDEA-0095`  
Sources: SRC-0160, SRC-0156

## Cheap first run

Choose explicit/latent/flow-latent modes under cost and mismatch.

## Baselines

- all explicit
- all latent
- flow latent
- entropy threshold
- mismatch aware
- budget aware
- oracle

## Metrics

- expected_success
- cost_fraction
- catastrophic_failure
- utility

## Stop condition

If extremes dominate across calibrated regimes, router not interesting.

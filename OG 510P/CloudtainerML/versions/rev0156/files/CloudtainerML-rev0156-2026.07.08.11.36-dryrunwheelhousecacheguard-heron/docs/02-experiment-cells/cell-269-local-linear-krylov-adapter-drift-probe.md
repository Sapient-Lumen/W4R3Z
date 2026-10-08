# CELL-269 — Local-Linear Krylov Adapter Drift Probe

Priority: **P1**  
Status: `future-trained-tiny`  
Sources: SRC-0150

## Question

Do useful adaptation subspaces drift over training so static low-rank adapters become stale?

## Cheap first run

Track adapter subspaces during a shifting synthetic task and measure stale-basis regret.

## Metrics

- `subspace_angle`
- `loss`
- `regret`
- `rank`

## Required baselines

- `static_basis`
- `sliding_basis`
- `oracle_retrained_basis`

## Stop condition

Promote if basis drift strongly predicts adaptation failure.

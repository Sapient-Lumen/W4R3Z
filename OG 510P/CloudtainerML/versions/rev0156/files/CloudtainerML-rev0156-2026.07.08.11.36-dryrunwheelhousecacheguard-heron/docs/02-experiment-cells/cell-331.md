# CELL-331 — Tiny Routing Absorption Trained Probe

Priority: **P0**  
Status: **trained-probe-added**

## Question

When a sparse gate is trained jointly with attention, does soft training accuracy survive hard top-k deployment, or is posthoc gating over frozen dense geometry more reliable?

## Cheap first run

Train lookup/copy models and compare soft end-to-end gate, hard deployed gate, posthoc hard gate, dense, random sparse, and oracle sparse.

## Metrics

- `accuracy`
- `loss`
- `target_keep`
- `target_miss`
- `deployment_gap`
- `gate_entropy`
- `cost`
- `score`

## Required baselines

- `dense_full`
- `random_sparse`
- `oracle_sparse`
- `posthoc_gate_hard`

## Stop condition

Promote only if hard-gate and posthoc results expose a mechanism not visible in soft training accuracy.

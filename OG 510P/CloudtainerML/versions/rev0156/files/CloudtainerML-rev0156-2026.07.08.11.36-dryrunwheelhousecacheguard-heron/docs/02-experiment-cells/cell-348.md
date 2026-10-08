# CELL-348 — Trained Mechanism Guard Report

Priority: **P0**  
Status: **audit-refactor-added**

## Question

Are trained tiny probes carrying the same exactness, sparsity, routing/gain and deployment guard fields as symbolic probes?

## Cheap first run

Run tools/trained_mechanism_guard_report.py over current revision trained outputs.

## Metrics

- `trained_artifact_count`
- `guard_ready_count`
- `exactness_ready_count`
- `route_gain_ready_count`
- `sparsity_ready_count`

## Required baselines

- `trained_escalation_report`
- `mechanism_promotion_report`
- `exactness_guard_report`

## Stop condition

Trained toy probes should not be promoted on accuracy alone; guard fields must travel with the result.

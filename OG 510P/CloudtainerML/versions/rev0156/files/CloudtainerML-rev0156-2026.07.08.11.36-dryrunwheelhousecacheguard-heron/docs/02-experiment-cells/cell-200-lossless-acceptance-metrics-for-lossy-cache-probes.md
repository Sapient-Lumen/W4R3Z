# CELL-200 — Lossless Acceptance Metrics for Lossy Cache Probes

Priority: **P0**  
Status: **candidate_refactor**  
Idea: `IDEA-0199`  
Sources: SRC-0228, SRC-0233

## Cheap first run

Add catastrophic-tail fields to existing probe outputs and dashboard.

## Metrics

- catastrophic divergence
- exact-output mismatch
- tail error quantiles
- mean error

## Required baselines

- current mean metric
- tail-aware metric
- oracle exact output

## Stop condition

If tail metrics do not change rankings, keep dashboards simpler.

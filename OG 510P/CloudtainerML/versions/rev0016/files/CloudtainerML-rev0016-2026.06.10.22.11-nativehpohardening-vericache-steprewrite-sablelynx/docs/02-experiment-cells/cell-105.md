# CELL-105 — Probe Metric Index Refactor

Priority: **P0**  
Status: **runnable**  
Idea: `IDEA-0105`  
Sources: SRC-0153, SRC-0154, SRC-0133, SRC-0160

## Cheap first run

Scan probe outputs for primary metrics and schema readiness.

## Baselines

- old dashboard
- metric index
- strict schema validator

## Metrics

- metric_ready_count
- needs_schema_patch
- row_total
- discoverability

## Stop condition

If too heuristic, require strict primary_metric in smoke outputs.

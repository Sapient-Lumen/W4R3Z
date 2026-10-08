# CELL-335 — Sparse Attention Program Schema Scout

Priority: **P1**  
Status: **scouted**

## Question

Can sparse attention mechanisms be represented as small source/write-back/reuse programs so C++ wind tunnels become comparable rather than bespoke?

## Cheap first run

Inventory existing sparse mechanisms as source sets, write-back sets, reuse/carry rules, and termination rules.

## Metrics

- `schema_coverage`
- `guard_field_coverage`
- `mechanism_exceptions`

## Required baselines

- `native_probe_index`
- `operator_route_report`

## Stop condition

Promote only if it reduces bespoke probe code or improves report comparability.

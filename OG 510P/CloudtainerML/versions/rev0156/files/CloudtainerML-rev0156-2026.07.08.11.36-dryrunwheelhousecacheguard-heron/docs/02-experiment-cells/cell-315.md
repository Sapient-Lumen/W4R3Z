# CELL-315 — Spectral Operator Report Refactor

Priority: **P0**  
Status: `audit-refactor`

## Why it exists

Can the cube compare spectral/operator probes separately from generic router and native dashboards?

## Cheap first run

Run tools/spectral_operator_report.py; compare spectral/operator artifacts by freshness, guard fields, and readiness.

## Metrics

- `spectral_family_artifacts`
- `fresh_spectral_artifacts`
- `readiness`
- `winner_diversity`
- `alias_field`
- `tail_field`
- `regret_field`

## Required baselines

- `operator_route_report`
- `performance_hardening_report`
- `native_phase_readiness_report`

## Stop condition

Delete if it does not change next-step priorities.

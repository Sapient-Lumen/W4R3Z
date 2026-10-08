# CELL-302 — Native Phase Readiness Report Refactor

Priority: **P0**  
Status: `audit-refactor`

## Why this exists
tools/native_phase_readiness_report.py scores fresh native outputs for guard fields, diversity, rows, and promotion-readiness.

## Metrics
- fresh outputs
- guard fields
- winner diversity
- row count
- readiness score

## Required baselines
- performance_hardening_report
- screen_regret_report
- native_probe_index

## Stop condition
If fresh probes lack guard fields, block promotion.

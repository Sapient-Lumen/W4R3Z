# CELL-293 — Performance Hardening Report Refactor

Priority: **P0**  
Status: **audit-refactor**

## Why this cell exists
New tool tools/performance_hardening_report.py summarizes fresh outputs, guard fields, winner-collapse warnings, and promotion readiness.

## Question
Linked idea: `IDEA-0244`.

## Sources
- audit/refactor internal

## Metrics
- fresh outputs
- guard field count
- winner diversity
- collapse warnings

## Required baselines
- performance_promotion_report
- screen_regret_report
- native_probe_index

## Stop condition
If fresh probes can win without cost/tail/regret fields, keep hardening the report.

## Rev0027 note
Performance-first lane. Security/trust side-wing material is not driving this cell.

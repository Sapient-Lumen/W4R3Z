# CELL-293 — Performance Hardening Report Refactor

Priority: **P0**  
Status: **audit-refactor**

## Cheap first run
New tool tools/performance_hardening_report.py summarizes fresh outputs, guard fields, winner-collapse warnings, and promotion readiness.

## Linked idea
`IDEA-0244`

## Sources
- audit/refactor internal

## Metrics
- fresh outputs
- guard field count
- winner diversity
- collapse warnings

## Stop condition
If fresh probes can win without cost/tail/regret fields, keep hardening the report.

## Rev0027 note
Performance-first cell; security/trust side-wing is not driving this priority.

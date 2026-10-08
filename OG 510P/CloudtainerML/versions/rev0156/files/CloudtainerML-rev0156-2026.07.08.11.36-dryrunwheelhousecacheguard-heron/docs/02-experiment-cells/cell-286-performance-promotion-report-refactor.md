# CELL-286 — Performance Promotion Report Refactor

Priority: **P0**  
Status: **audit-refactor**

## Why this cell exists
New audit tool tools/performance_promotion_report.py summarizes current native probes by primary metric, regret/cost fields, and promotion readiness.

## Metrics
- fresh/carry-forward status
- guard fields
- primary metric presence
- promotion readiness

## Stop condition
If the report cannot distinguish fresh runnable probes from carry-forward artifacts, keep hardening.

## Rev0026 focus
Performance-core / tiny architecture-surprise lane. Security/trust material is a bounded side wing, not the project center.

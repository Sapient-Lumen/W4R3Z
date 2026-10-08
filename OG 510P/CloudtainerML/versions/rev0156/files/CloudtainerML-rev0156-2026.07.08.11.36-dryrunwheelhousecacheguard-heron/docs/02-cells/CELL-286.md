# CELL-286 — Performance Promotion Report Refactor

Priority: **P0**  
Status: **audit-refactor**

## Why this cell exists
New audit tool tools/performance_promotion_report.py summarizes current native probes by primary metric, regret/cost fields, and promotion readiness.

## Question
Linked idea: `IDEA-0244`.

## Sources
audit/refactor internal

## Metrics
- fresh/carry-forward status
- guard fields
- primary metric presence
- promotion readiness

## Stop condition
If the report cannot distinguish fresh runnable probes from carry-forward artifacts, keep hardening.

## Rev0026 note
This cell keeps CloudtainerML centered on tiny-scale performance/surprise. Security/trust side-wing material is not driving this priority.

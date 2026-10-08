# Structural audit rev0312 — MVR, score-state correction, public-signal validator

Created: 2026-06-04T07:03:56-04:00

## Highest-risk correction

rev0311's adjudicated scorecard was useful but had a serious scoring defect: 60 of 124 rows did not have state counts that summed back to `gate_rows`. The failure mode was usually verified-current counts coexisting with missing counts on the same score row. rev0312 recomputes the scorecard from mutually exclusive `local_status` values and marks the rev0311 adjudicated scorecard as historical input only.

## Operational focus

rev0312 adds 12 minimum viable readiness thresholds. A green claim is blocked unless alerting, ROP EP PI reconciliation, route/ETE capacity, institutional/no-car/AFN movement, CRC throughput, KI anti-theater, ingestion controls, recovery/claims, AAR/corrective-action closure, advanced-reactor performance branch, and public-claim safety all have real evidence.

## Refactor/audit performed

The package now routes readiness queries through:

`sparse applicability -> local evidence -> corrected scorecard -> public-signal validator -> MVR gate -> compact blocker workpack`

The three 114,494-row universal crossproduct tables remain compatibility resources only.

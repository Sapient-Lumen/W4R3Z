# Synthetic election-event log reconciliation

Archive version: `v900`  
Report: `artifacts/reports/election-event-log-reconciliation-rev0900.json`  
Decision: `SYNTHETIC_EVENT_LOG_CHAIN_PASS_NOT_LIVE_EEL`  

This synthetic check binds the Example County CDF replay and ballot-accounting outputs into a chronological event chain with per-artifact SHA-256 digests.

## Counts

- Events checked: `12`.
- Required artifact roles: `12`.
- Missing required roles: `0`.
- Artifact digest matches: `12`.
- Errors: `0`.

## Boundary

This is not live Election Event Log evidence, not full NIST EEL or CDF conformance, not the NIST CDF Test Method, not certification, not outcome proof, not current voter instruction, and not legal advice.
It does not authorize live pilot use and does not replace custody transfer/seal records, access logs, audit, recount, canvass, certification, retention, public-records review, or counsel review.

# 586 — Nuclear emergency preparedness: dispatch workorders, response-intake CLI, and verified route targets

Revision: rev0379  
Base: rev0378  
Status: canon  
Claim posture: operator-ready dispatch kit built / route targets verified / response-intake CLI added / active-surface refocused / no request sent / no readiness conclusion

## Substance-first priority

Rev0379 addresses the next execution risk: the cube has enough request language, but it still lacked a disciplined operator path for sending the current batch, capturing the exact receipt, hashing responses, and preventing stale or duplicate dispatch. This revision converts the rev0378 canonical batch into workorders and a response-import harness.

## Priority changes made

- Added `records-requests/bvps-rev0379/operator-submit-board-rev0379.csv` as the current route-verified dispatch board.
- Added one workorder per active request under `records-requests/bvps-rev0379/workorders/`.
- Added `records-requests/bvps-rev0379/operator-submit-payloads-rev0379.csv` and `operator-submit-runbook-rev0379.md` for copy/paste execution.
- Added one rev0379 receipt sidecar per active request under `evidence-intake/bvps-rev0379/receipt-sidecars/`.
- Added `tools/bvps_response_intake_rev0379.py`, a local response/receipt importer that validates request IDs, copies files into request-specific import folders, writes SHA-256 manifests, and appends the import manifest to the sidecar.
- Added `cube/bvps-route-target-verification-rev0379.csv`, `cube/bvps-dispatch-workorder-board-rev0379.csv`, `cube/bvps-post-dispatch-wait-state-board-rev0379.csv`, and `cube/bvps-response-sidecar-board-rev0379.csv`.
- Rebuilt normalized `cube/file.csv`, `cube/file-field-value.csv`, `cube/file-tag-edge-normalized.csv`, `cube/source-use-ledger.csv`, `cube/source-edge-table.csv`, and `cube/file-source-edge.csv` through file 586.

## Route findings that changed behavior

The DHS/FEMA federal route must remain online-only; the current FOIA.gov/FEMA component surface warns that DHS is no longer accepting mailed or emailed FOIA/Privacy Act requests for DHS records. The NRC route should search ADAMS Public Search first because NRC says APS is the latest public interface and Web-Based ADAMS has been retired. PEMA, Ohio DPS/GovQA, West Virginia custodian law, Hancock County OEM, Beaver County AFN/emergency information, and Columbiana ENS/IPAWS plan surfaces are now attached to request workorders as route/context sources.

## Audit/refactor performed

The active surface is cut to a dispatch/intake set: route targets, workorders, canonical request text, sidecar templates, the response-import CLI, active proofcut boards, and validators. Historical request generations and older validation mirrors remain in the full archive but are not in the active capsule. This is a non-destructive refactor intended to reduce scan time and prevent an operator from accidentally treating old request packets as current.

## Non-claims

- No records request has been sent from this static archive.
- No dispatch receipt has been imported.
- No official FEMA Region 3 preliminary-findings packet has been imported.
- No official FEMA Region 5 / Ohio / Columbiana results packet has been imported.
- No West Virginia / Hancock County response packet has been imported.
- No EN58200 EOF repair/retest/CAP closure packet has been imported.
- No ANS/ENS/IPAWS, AFN/language, public-information, CAP/retest, EOF, or local readiness proofcut is closed.
- No local readiness conclusion is made.

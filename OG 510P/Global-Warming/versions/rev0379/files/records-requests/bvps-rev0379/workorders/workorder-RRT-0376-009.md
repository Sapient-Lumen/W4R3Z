# Workorder — RRT-0376-009

Status: ready-not-sent / operator action required  
Revision: rev0379  
Custodian: Columbiana County EMA  
Jurisdiction: ohio_county_public_records  
Canonical request file: `records-requests/bvps-rev0376/rrt-0376-009-columbiana-ema-ens-ipaws-current-plan-exercise-logs.md`  
Request SHA-256: `68e759e5167642d0fe16e9dba15d941c30a1d00ba8ca19b22d6a60863c371506`  
Route URL / target: https://ccoema.org/images/pdf/2026Forms/RERP%20Rev%2038%202026.pdf  
Route source IDs: S1406;S1374;S1378  
Receipt sidecar to complete: `evidence-intake/bvps-rev0379/receipt-sidecars/sidecar-RRT-0376-009.md`  
Claim boundary: this workorder is not evidence of readiness, dispatch, response, or proofcut closure.

## Send gate

1. Confirm this request ID is present in `records-requests/bvps-rev0379/operator-submit-board-rev0379.csv` with `dispatch_status=ready_not_sent`.
2. Open the canonical request file and copy only its request text or upload it as the portal permits.
3. If the portal forces a narrower form, preserve the exact text actually submitted as a receipt artifact.
4. Submit once. Do not also send superseded packets for the same proofcut.

## Targeted proofcuts

Columbiana_11am_results;ENS_IPAWS_EAS_WEA_siren;AFN_language;hotwash_CAP

## Immediate after-submit actions

- Save the confirmation page/email/ticket as a file.
- Record the submitted timestamp, timezone, route, ticket number, and exact submitted text hash.
- Place receipt artifacts under `evidence-intake/bvps-rev0379/inbox/RRT-0376-009/`.
- Run `python tools/bvps_response_intake_rev0379.py --root . --request-id RRT-0376-009 --input-dir evidence-intake/bvps-rev0379/inbox/RRT-0376-009`.
- Complete `evidence-intake/bvps-rev0379/receipt-sidecars/sidecar-RRT-0376-009.md` before any proofcut adjudication.

## Do-not-claim rule

Dispatch, acknowledgement, fee notices, route redirects, or public-plan language do not close any proofcut. A proofcut needs substantive response records, hashes, DLP status, and mapping to the proofcut matrix.

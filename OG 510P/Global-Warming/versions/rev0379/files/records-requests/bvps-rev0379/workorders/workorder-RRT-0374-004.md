# Workorder — RRT-0374-004

Status: ready-not-sent / operator action required  
Revision: rev0379  
Custodian: Beaver County Emergency Services / Open Records  
Jurisdiction: pennsylvania_county_RTKL  
Canonical request file: `records-requests/bvps-rev0374/rrt-0374-004-beaver-county-open-records-warning-afn-local-logs.md`  
Request SHA-256: `23672def38a4b48a8954ffcb298fee3b34a3dcbd32ba9a2fdd07cb66dc26a9bb`  
Route URL / target: https://www.beavercountypa.gov/departments/emergency-services/beaver-valley-power-station-emergency-information  
Route source IDs: S1405;S1368  
Receipt sidecar to complete: `evidence-intake/bvps-rev0379/receipt-sidecars/sidecar-RRT-0374-004.md`  
Claim boundary: this workorder is not evidence of readiness, dispatch, response, or proofcut closure.

## Send gate

1. Confirm this request ID is present in `records-requests/bvps-rev0379/operator-submit-board-rev0379.csv` with `dispatch_status=ready_not_sent`.
2. Open the canonical request file and copy only its request text or upload it as the portal permits.
3. If the portal forces a narrower form, preserve the exact text actually submitted as a receipt artifact.
4. Submit once. Do not also send superseded packets for the same proofcut.

## Targeted proofcuts

Beaver_local_EOC;warning_logs;AFN;CAP_retest

## Immediate after-submit actions

- Save the confirmation page/email/ticket as a file.
- Record the submitted timestamp, timezone, route, ticket number, and exact submitted text hash.
- Place receipt artifacts under `evidence-intake/bvps-rev0379/inbox/RRT-0374-004/`.
- Run `python tools/bvps_response_intake_rev0379.py --root . --request-id RRT-0374-004 --input-dir evidence-intake/bvps-rev0379/inbox/RRT-0374-004`.
- Complete `evidence-intake/bvps-rev0379/receipt-sidecars/sidecar-RRT-0374-004.md` before any proofcut adjudication.

## Do-not-claim rule

Dispatch, acknowledgement, fee notices, route redirects, or public-plan language do not close any proofcut. A proofcut needs substantive response records, hashes, DLP status, and mapping to the proofcut matrix.

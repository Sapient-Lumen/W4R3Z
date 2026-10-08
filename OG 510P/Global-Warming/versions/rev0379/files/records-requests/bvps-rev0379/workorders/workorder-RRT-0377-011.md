# Workorder — RRT-0377-011

Status: ready-not-sent / operator action required  
Revision: rev0379  
Custodian: WV DHS / WV Emergency Management Division  
Jurisdiction: west_virginia_FOIA  
Canonical request file: `records-requests/bvps-rev0377/rrt-0377-011-wv-dhs-wvemd-hancock-bvps-exercise-evaluator-materials.md`  
Request SHA-256: `8a88a69855166a90764930f5ec72f5458fee1311e25e5288f5cb28733236761c`  
Route URL / target: https://code.wvlegislature.gov/29B-1-3/  
Route source IDs: S1403;S1388;S1389;S1390  
Receipt sidecar to complete: `evidence-intake/bvps-rev0379/receipt-sidecars/sidecar-RRT-0377-011.md`  
Claim boundary: this workorder is not evidence of readiness, dispatch, response, or proofcut closure.

## Send gate

1. Confirm this request ID is present in `records-requests/bvps-rev0379/operator-submit-board-rev0379.csv` with `dispatch_status=ready_not_sent`.
2. Open the canonical request file and copy only its request text or upload it as the portal permits.
3. If the portal forces a narrower form, preserve the exact text actually submitted as a receipt artifact.
4. Submit once. Do not also send superseded packets for the same proofcut.

## Targeted proofcuts

WV_state_EOC;Hancock_coordination;Region3_findings;CAP_retest;AFN_language

## Immediate after-submit actions

- Save the confirmation page/email/ticket as a file.
- Record the submitted timestamp, timezone, route, ticket number, and exact submitted text hash.
- Place receipt artifacts under `evidence-intake/bvps-rev0379/inbox/RRT-0377-011/`.
- Run `python tools/bvps_response_intake_rev0379.py --root . --request-id RRT-0377-011 --input-dir evidence-intake/bvps-rev0379/inbox/RRT-0377-011`.
- Complete `evidence-intake/bvps-rev0379/receipt-sidecars/sidecar-RRT-0377-011.md` before any proofcut adjudication.

## Do-not-claim rule

Dispatch, acknowledgement, fee notices, route redirects, or public-plan language do not close any proofcut. A proofcut needs substantive response records, hashes, DLP status, and mapping to the proofcut matrix.

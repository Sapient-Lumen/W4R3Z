# Workorder — RRT-0374-003

Status: ready-not-sent / operator action required  
Revision: rev0379  
Custodian: PEMA  
Jurisdiction: pennsylvania_RTKL  
Canonical request file: `records-requests/bvps-rev0374/rrt-0374-003-pema-rtkl-ans-exercise-afn-capa.md`  
Request SHA-256: `6447476b4371cf74d2c2adefbab7e28c8709e185978dfd5a60eb757ff710d7f4`  
Route URL / target: https://www.pa.gov/services/pema/rtk-request-pema  
Route source IDs: S1402;S1367;S1372  
Receipt sidecar to complete: `evidence-intake/bvps-rev0379/receipt-sidecars/sidecar-RRT-0374-003.md`  
Claim boundary: this workorder is not evidence of readiness, dispatch, response, or proofcut closure.

## Send gate

1. Confirm this request ID is present in `records-requests/bvps-rev0379/operator-submit-board-rev0379.csv` with `dispatch_status=ready_not_sent`.
2. Open the canonical request file and copy only its request text or upload it as the portal permits.
3. If the portal forces a narrower form, preserve the exact text actually submitted as a receipt artifact.
4. Submit once. Do not also send superseded packets for the same proofcut.

## Targeted proofcuts

PA_state_evaluator_packet;ANS_IPAWS;AFN_language;CAP_retest

## Immediate after-submit actions

- Save the confirmation page/email/ticket as a file.
- Record the submitted timestamp, timezone, route, ticket number, and exact submitted text hash.
- Place receipt artifacts under `evidence-intake/bvps-rev0379/inbox/RRT-0374-003/`.
- Run `python tools/bvps_response_intake_rev0379.py --root . --request-id RRT-0374-003 --input-dir evidence-intake/bvps-rev0379/inbox/RRT-0374-003`.
- Complete `evidence-intake/bvps-rev0379/receipt-sidecars/sidecar-RRT-0374-003.md` before any proofcut adjudication.

## Do-not-claim rule

Dispatch, acknowledgement, fee notices, route redirects, or public-plan language do not close any proofcut. A proofcut needs substantive response records, hashes, DLP status, and mapping to the proofcut matrix.

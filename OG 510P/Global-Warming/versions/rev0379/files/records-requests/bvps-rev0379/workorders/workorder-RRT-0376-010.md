# Workorder — RRT-0376-010

Status: ready-not-sent / operator action required  
Revision: rev0379  
Custodian: Ohio DPS / Ohio EMA  
Jurisdiction: ohio_public_records  
Canonical request file: `records-requests/bvps-rev0376/rrt-0376-010-ohio-dps-public-records-center-ema-ens-ipaws-exercise-logs.md`  
Request SHA-256: `a6551b4f19086d6a9664ad61cb557012c41ae0440b94d63cbc6dcecc56dbf3dc`  
Route URL / target: https://publicsafetyohio.govqa.us/WEBAPP/_rs/SupportHome.aspx?lp=4  
Route source IDs: S1407;S1386;S1387  
Receipt sidecar to complete: `evidence-intake/bvps-rev0379/receipt-sidecars/sidecar-RRT-0376-010.md`  
Claim boundary: this workorder is not evidence of readiness, dispatch, response, or proofcut closure.

## Send gate

1. Confirm this request ID is present in `records-requests/bvps-rev0379/operator-submit-board-rev0379.csv` with `dispatch_status=ready_not_sent`.
2. Open the canonical request file and copy only its request text or upload it as the portal permits.
3. If the portal forces a narrower form, preserve the exact text actually submitted as a receipt artifact.
4. Submit once. Do not also send superseded packets for the same proofcut.

## Targeted proofcuts

Ohio_state_EOC;ENS_IPAWS;Region5_findings;CAP_retest

## Immediate after-submit actions

- Save the confirmation page/email/ticket as a file.
- Record the submitted timestamp, timezone, route, ticket number, and exact submitted text hash.
- Place receipt artifacts under `evidence-intake/bvps-rev0379/inbox/RRT-0376-010/`.
- Run `python tools/bvps_response_intake_rev0379.py --root . --request-id RRT-0376-010 --input-dir evidence-intake/bvps-rev0379/inbox/RRT-0376-010`.
- Complete `evidence-intake/bvps-rev0379/receipt-sidecars/sidecar-RRT-0376-010.md` before any proofcut adjudication.

## Do-not-claim rule

Dispatch, acknowledgement, fee notices, route redirects, or public-plan language do not close any proofcut. A proofcut needs substantive response records, hashes, DLP status, and mapping to the proofcut matrix.

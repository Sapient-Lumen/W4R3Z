# Workorder — RRT-0377-012

Status: ready-not-sent / operator action required  
Revision: rev0379  
Custodian: Hancock County WV OEM / 911  
Jurisdiction: west_virginia_county_FOIA  
Canonical request file: `records-requests/bvps-rev0377/rrt-0377-012-hancock-county-oem-bvps-exercise-alerting-eoc-afn-capa.md`  
Request SHA-256: `328aabbeec751118c2b14b80e66970392254a14adb9d293464263dcbf6f363f0`  
Route URL / target: https://hancockcountywv.org/oem.html  
Route source IDs: S1404;S1403;S1391;S1392  
Receipt sidecar to complete: `evidence-intake/bvps-rev0379/receipt-sidecars/sidecar-RRT-0377-012.md`  
Claim boundary: this workorder is not evidence of readiness, dispatch, response, or proofcut closure.

## Send gate

1. Confirm this request ID is present in `records-requests/bvps-rev0379/operator-submit-board-rev0379.csv` with `dispatch_status=ready_not_sent`.
2. Open the canonical request file and copy only its request text or upload it as the portal permits.
3. If the portal forces a narrower form, preserve the exact text actually submitted as a receipt artifact.
4. Submit once. Do not also send superseded packets for the same proofcut.

## Targeted proofcuts

Hancock_local_EOC;alerting;AFN_language;hotwash_CAP;resource_logs

## Immediate after-submit actions

- Save the confirmation page/email/ticket as a file.
- Record the submitted timestamp, timezone, route, ticket number, and exact submitted text hash.
- Place receipt artifacts under `evidence-intake/bvps-rev0379/inbox/RRT-0377-012/`.
- Run `python tools/bvps_response_intake_rev0379.py --root . --request-id RRT-0377-012 --input-dir evidence-intake/bvps-rev0379/inbox/RRT-0377-012`.
- Complete `evidence-intake/bvps-rev0379/receipt-sidecars/sidecar-RRT-0377-012.md` before any proofcut adjudication.

## Do-not-claim rule

Dispatch, acknowledgement, fee notices, route redirects, or public-plan language do not close any proofcut. A proofcut needs substantive response records, hashes, DLP status, and mapping to the proofcut matrix.

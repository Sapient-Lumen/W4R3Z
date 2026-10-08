# Workorder — RRT-0378-013

Status: ready-not-sent / operator action required  
Revision: rev0379  
Custodian: DHS/FEMA consolidated: Region 3, Region 5, REP program  
Jurisdiction: federal_FOIA  
Canonical request file: `records-requests/bvps-rev0378/rrt-0378-013-dhs-fema-consolidated-tristate-bvps-exercise-findings-ipaws.md`  
Request SHA-256: `7d28e5c920cb9f8b557d617e27438e5f2f03726ea9e5e1364022d22cae734539`  
Route URL / target: https://www.foia.gov/agency-search.html?id=716e47df-ec30-4748-9b53-0055746b9490&type=component  
Route source IDs: S1400;S1398;S1399  
Receipt sidecar to complete: `evidence-intake/bvps-rev0379/receipt-sidecars/sidecar-RRT-0378-013.md`  
Claim boundary: this workorder is not evidence of readiness, dispatch, response, or proofcut closure.

## Send gate

1. Confirm this request ID is present in `records-requests/bvps-rev0379/operator-submit-board-rev0379.csv` with `dispatch_status=ready_not_sent`.
2. Open the canonical request file and copy only its request text or upload it as the portal permits.
3. If the portal forces a narrower form, preserve the exact text actually submitted as a receipt artifact.
4. Submit once. Do not also send superseded packets for the same proofcut.

## Targeted proofcuts

Region3_PA_WV_findings;Region5_OH_findings;public_meeting_530pm;Columbiana_11am_results;ANS_ENS_IPAWS_EAS_WEA_siren;AFN_language;CAP_retest

## Immediate after-submit actions

- Save the confirmation page/email/ticket as a file.
- Record the submitted timestamp, timezone, route, ticket number, and exact submitted text hash.
- Place receipt artifacts under `evidence-intake/bvps-rev0379/inbox/RRT-0378-013/`.
- Run `python tools/bvps_response_intake_rev0379.py --root . --request-id RRT-0378-013 --input-dir evidence-intake/bvps-rev0379/inbox/RRT-0378-013`.
- Complete `evidence-intake/bvps-rev0379/receipt-sidecars/sidecar-RRT-0378-013.md` before any proofcut adjudication.

## Do-not-claim rule

Dispatch, acknowledgement, fee notices, route redirects, or public-plan language do not close any proofcut. A proofcut needs substantive response records, hashes, DLP status, and mapping to the proofcut matrix.

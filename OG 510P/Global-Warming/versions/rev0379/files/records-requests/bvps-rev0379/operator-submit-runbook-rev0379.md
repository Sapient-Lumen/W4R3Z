# Rev0379 operator submit runbook — move from paper readiness to actual dispatch receipts

Status: ready-not-sent  
Generated: 2026-06-12T23:50:00-04:00  
Claim boundary: this runbook is not dispatch proof and not emergency-preparedness evidence.

## Core rule

Use only `records-requests/bvps-rev0379/operator-submit-board-rev0379.csv` and the workorders under `records-requests/bvps-rev0379/workorders/`. Do not send older request packets unless a workorder explicitly points to them as the canonical request text.

## Execution order

1. Send `RRT-0378-013` through the DHS/FEMA online FOIA route.
2. Search ADAMS APS, then send `RRT-0378-014` through NRC FOIA/PDR if records are not already public.
3. Send the state/local packets in board order: PEMA, Beaver County, Ohio DPS/Ohio EMA, Columbiana County EMA, WV DHS/WVEMD, Hancock County OEM.
4. After each send, save the confirmation/receipt into `evidence-intake/bvps-rev0379/inbox/<request-id>/`.
5. Run `tools/bvps_response_intake_rev0379.py` for that request ID.
6. Fill the sidecar fields that automation cannot know: route, ticket number, submitted text hash, response type, DLP status, proofcut mapping.

## Immediate stop conditions

- The portal/contact route has materially changed.
- A portal refuses consolidated text and forces narrowed categories.
- A response includes personal, security-sensitive, credential, or medical information.
- A custodian redirects the request.

In those cases, save the evidence as a response artifact and do not claim proofcut progress until the sidecar records the exception.

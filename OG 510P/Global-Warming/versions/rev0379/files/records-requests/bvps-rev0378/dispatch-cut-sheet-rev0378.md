# Rev0378 canonical dispatch cut sheet — send only the active batch

Status: ready-not-sent  
Generated: 2026-06-12T23:16:00-04:00  
Claim boundary: dispatch, receipts, and acknowledgements are not readiness evidence.

## Why this exists

The prior package had many request packets across rev0370–rev0377. That created a duplicate-dispatch risk: an operator could submit stale or overlapping requests and lose the clean chain of custody. Rev0378 promotes a canonical active batch and records older packets as superseded or lineage-only.

## Active dispatch batch

Use `records-requests/bvps-rev0378/canonical-dispatch-batch-rev0378.csv`. Send in this order unless a custodian route fails:

1. RRT-0378-013 — DHS/FEMA consolidated tri-state BVPS exercise findings and alerting/IPAWS packet.
2. RRT-0378-014 — NRC ADAMS/FOIA EN58200 EOF repair/retest/CAP and REP transmittal packet.
3. RRT-0374-003 — PEMA RTKL packet.
4. RRT-0374-004 — Beaver County packet.
5. RRT-0376-010 — Ohio DPS / Ohio EMA portal packet.
6. RRT-0376-009 — Columbiana County EMA packet.
7. RRT-0377-011 — WV DHS / WV Emergency Management Division packet.
8. RRT-0377-012 — Hancock County OEM packet.

## Immediately after each submission

1. Save the receipt page, confirmation email, ticket number, or sent-message proof.
2. Hash the receipt artifact.
3. Fill the matching sidecar in `evidence-intake/bvps-rev0378/receipt-sidecars/`.
4. Replace the estimated clock in `cube/bvps-dispatch-deadline-clock-rev0378.csv` with the actual custodian receipt timestamp.
5. Do not make a readiness claim.

## Watch dates if received on Monday 2026-06-15

- Federal FEMA/NRC FOIA control due estimate: 2026-07-14.
- Pennsylvania/WV five-business-day control estimate: 2026-06-22.
- Ohio follow-up control estimate: 2026-06-22, with second watch on 2026-06-29; Ohio has no fixed day-count clock in this cut sheet.

## Dispatch hygiene

- Do not dispatch requests marked `superseded_do_not_dispatch` in `cube/records-request-supersession-ledger-rev0378.csv`.
- If a portal forces narrowed text, save the exact portal submission as the controlling copy.
- If a custodian redirects the request, preserve the redirect message as a response artifact and file the corrected request with a new sidecar entry.

# 584 — Nuclear emergency preparedness: West Virginia/Hancock lane repair, tri-state dispatch board, and active-surface cut

Revision: rev0377  
Base: rev0376  
Status: canon  
Claim posture: West Virginia/Hancock acquisition lane repaired / tri-state dispatch board created / active surface cut / claim-frozen / no local readiness conclusion

## Substance-first priority

Rev0377 works the largest remaining acquisition gap instead of adding doctrine. The FEMA exercise notice names Pennsylvania and West Virginia, and prior revisions had Pennsylvania, Ohio/Columbiana, FEMA, and NRC request lanes. The West Virginia lane was still too implicit. That is risky because a Region 3 packet can look complete while missing Hancock County and West Virginia state records that may hold local EOC, public-warning, AFN/language, hotwash, corrective-action, and state coordination evidence.

This revision adds a West Virginia state packet and a Hancock County packet, puts them onto a single tri-state dispatch board, and attaches statutory/follow-up clocks so the next operator can dispatch and then track receipts rather than redraft.

## Priority changes made

- Added `records-requests/bvps-rev0377/rrt-0377-011-wv-dhs-wvemd-hancock-bvps-exercise-evaluator-materials.md`.
- Added `records-requests/bvps-rev0377/rrt-0377-012-hancock-county-oem-bvps-exercise-alerting-eoc-afn-capa.md`.
- Added `records-requests/bvps-rev0377/dispatch-cut-sheet-rev0377.md` and `records-requests/bvps-rev0377/dispatch-board-rev0377.csv`.
- Added `cube/bvps-wv-hancock-route-gap-audit-rev0377.csv` to record the defect and repair.
- Added `cube/bvps-tristate-custodian-dispatch-board-rev0377.csv` so FEMA Region 3, WV/WVEMD, Hancock County, PEMA, Beaver County, FEMA Region 5, Columbiana, Ohio DPS/Ohio EMA, and NRC are visible in one operational surface.
- Added `cube/bvps-proofcut-dispatch-matrix-rev0377.csv` so each proofcut has a request owner and backup path.
- Added `cube/bvps-official-artifact-watch-rev0377.csv` to keep post-meeting public artifact searches from being mistaken for findings imports.
- Added `cube/records-request-packet-inventory-rev0377.csv` to hash and inventory all current request packets.
- Added `evidence-bags/bvps-tristate-dispatch-capsule-rev0377.zip` as a compact forward-work capsule.

## Audit/refactor performed

Rev0377 refactors the active surface around dispatch execution. The package still keeps historical luggage, but the active capsule now packages only the front door, current dispatch board, current request packets, source/index tables, response-gate context, and validators needed to execute the next human step. This reduces the chance that the next session spends time scanning old validation reports or duplicate historical field kits instead of sending and tracking records requests.

The refactor is deliberately non-destructive: no historical evidence is deleted, no prior validator is removed, and no records request is marked sent.

## Non-claims

- No real Beaver Valley response packet has been imported.
- No records request has been sent from this static archive.
- No official FEMA Region 3 preliminary-findings packet has been adjudicated.
- No official West Virginia or Hancock County response packet has been imported.
- No official Region 5 / Ohio / Columbiana results packet is imported.
- No ANS/ENS/IPAWS transition proofcut is closed.
- No AFN/language-access proofcut is closed.
- No EN58200 EOF repair/retest/corrective-action proofcut is closed.
- No local readiness conclusion is made.

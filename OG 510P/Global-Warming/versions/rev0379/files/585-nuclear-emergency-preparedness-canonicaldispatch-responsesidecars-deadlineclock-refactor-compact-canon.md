# 585 — Nuclear emergency preparedness: canonical dispatch batch, response sidecars, and deadline clock

Revision: rev0378  
Base: rev0377  
Status: canon  
Claim posture: canonical dispatch batch created / stale request dispatch risk reduced / response sidecars generated / deadline clock estimated / claim-frozen / no local readiness conclusion

## Substance-first priority

Rev0378 stops adding parallel request doctrine and turns the request sprawl into a controlled dispatch batch. The risk now is not that the cube lacks enough request text; it is that an operator could send the wrong stale packet, send overlapping federal requests, fail to save receipts, or import a response without the sidecar needed for proofcut credit.

This revision therefore creates two sharper federal packets and designates the active state/local packets that should remain in the live batch. It also marks older request packets as superseded or lineage-only, generates one receipt sidecar per active request, and creates deadline clocks that become real only after actual submission receipts are captured.

## Priority changes made

- Added `records-requests/bvps-rev0378/rrt-0378-013-dhs-fema-consolidated-tristate-bvps-exercise-findings-ipaws.md` to combine Region 3, Region 5, public-meeting, preliminary-findings, 11 a.m. results, and alerting/IPAWS requests into one federal FEMA/DHS dispatch path.
- Added `records-requests/bvps-rev0378/rrt-0378-014-nrc-adams-foia-en58200-eof-repair-retest-cap-and-rep-transmittals.md` to tighten the EN58200 EOF repair/retest/CAP closure ask and NRC/FEMA REP transmittal ask.
- Added `cube/bvps-canonical-dispatch-batch-rev0378.csv` and `records-requests/bvps-rev0378/canonical-dispatch-batch-rev0378.csv` as the controlling “send only these” board.
- Added `cube/records-request-supersession-ledger-rev0378.csv` so older request packets are not accidentally dispatched.
- Added `cube/bvps-dispatch-deadline-clock-rev0378.csv` with estimated clocks if requests are received Monday 2026-06-15; the table warns that receipts must replace estimates.
- Added `cube/bvps-response-sidecar-board-rev0378.csv` and request-specific receipt sidecars under `evidence-intake/bvps-rev0378/receipt-sidecars/`.
- Added `cube/bvps-official-artifact-search-log-rev0378.csv` recording that this session found notice/route artifacts but no imported official post-meeting findings packet or EN58200 closure packet.
- Added `evidence-bags/bvps-canonical-dispatch-capsule-rev0378.zip` as a smaller active surface focused on dispatch, receipts, and proofcut intake.

## Audit/refactor performed

Rev0378 refactors request history into three states: canonical active, superseded do-not-dispatch, and historical lineage. This is a non-destructive prune: old packets remain in the archive, but the active capsule and dispatch cut sheet point to the current batch only. The immediate goal is to prevent repeated drafting and force the next human action to be submission plus receipt capture.

## Non-claims

- No records request has been sent from this static archive.
- No dispatch receipt has been imported.
- No official FEMA Region 3 preliminary-findings packet has been imported.
- No official FEMA Region 5 / Ohio / Columbiana results packet has been imported.
- No West Virginia / Hancock County response packet has been imported.
- No EN58200 EOF repair/retest/CAP closure packet has been imported.
- No ANS/ENS/IPAWS, AFN/language, public-information, CAP/retest, EOF, or local readiness proofcut is closed.
- No local readiness conclusion is made.

# 582 — Nuclear emergency preparedness: FEMA region fork, request-cut upgrade, and validation-surface prune

Revision: rev0375  
Base: rev0374  
Status: canon  
Claim posture: Region 3/Region 5 acquisition split / official-findings watch sharpened / records packets upgraded / forward-work capsule built / validation-report mirror retention policy established / claim-frozen / no local readiness conclusion

## Substance-first priority

Rev0375 works the riskiest unfinished branch: post-exercise evidence can now split across different federal regions and different custodians. Rev0374 correctly split the 11:00 Columbiana results announcement from the 17:30 FEMA/IPAWS meeting, but it still allowed one dangerous assumption to persist: that the Ohio/Columbiana trail could ride on the same FEMA Region 3 path as Pennsylvania and West Virginia.

The new corrective action is a two-region acquisition tree. Pennsylvania and West Virginia remain tied to FEMA Region 3 notice/meeting/final-report channels; Ohio and Columbiana County now get an explicit FEMA Region 5 / Ohio EMA / Columbiana County branch. The route split is a work-control fact, not a readiness fact.

## Priority changes made

- Added `cube/bvps-fema-region-split-audit-rev0375.csv` to make the Region 3 vs Region 5 split explicit.
- Added `cube/bvps-official-findings-watchlist-rev0375.csv` to separate public-source watch from official imported evidence.
- Added `cube/bvps-request-specificity-upgrade-rev0375.csv` and `cube/bvps-proofcut-request-crosswalk-rev0375.csv` to sharpen each request against the proofcuts that remain open.
- Added three new ready-not-sent packets under `records-requests/bvps-rev0375/`:
  - `rrt-0375-006-fema-region-v-ohio-columbiana-results-briefing-and-evaluator-materials.md`
  - `rrt-0375-007-columbiana-county-ema-11am-results-briefing-evidence-packet.md`
  - `rrt-0375-008-ohio-ema-radiological-branch-bvps-exercise-ipaws-afn-capa.md`
- Added `records-requests/bvps-rev0375/dispatch-order-rev0375.md` so the next human action has a concrete send order and cannot drift back into doctrine writing.
- Built `evidence-bags/bvps-forward-work-capsule-rev0375.zip` as a smaller default surface for the next pass.

## Audit/refactor performed

Rev0375 performs a targeted region/custodian audit and a validation-surface refactor. The region audit prevents a false-negative acquisition path: a failure to ask FEMA Region 5 / Ohio records custodians could miss the 11:00 Columbiana results packet even if the Region 3/IPAWS path is eventually satisfied.

The validation-surface refactor is non-destructive. `cube/validation-report-retention-plan-rev0375.csv` marks historical validation reports for future archive/collapse, but the current revision does not delete evidence or history. The forward-work capsule is the actual friction-reducer: it carries only current packets, proofcuts, source-graph controls, and validators required for dispatch and response intake.

## Non-claims

- No real Beaver Valley response packet has been imported.
- No records request has been sent from this static archive.
- No official preliminary-findings packet has been adjudicated.
- No 11:00 Columbiana results packet is imported.
- No ANS/IPAWS transition proofcut is closed.
- No EN58200 EOF repair/retest/corrective-action proofcut is closed.
- No local readiness conclusion is made.

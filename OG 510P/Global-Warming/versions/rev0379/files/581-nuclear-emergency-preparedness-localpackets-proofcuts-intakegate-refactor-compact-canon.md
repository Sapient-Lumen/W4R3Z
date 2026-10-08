# 581 — Nuclear emergency preparedness: local packets, proofcut thresholds, intake gate, and active dispatch refactor

Revision: rev0374  
Base: rev0373  
Status: canon  
Claim posture: state-local packets ready / 11am results-capture fork open / proofcut thresholds explicit / DLP intake gate built / dispatch-intake capsule built / source graph synced through S1377 / claim-frozen / no local readiness conclusion

## Substance-first priority

Rev0374 focuses on the riskiest unfinished work: not losing the live/post-live Beaver Valley evidence trail. Rev0373 correctly prepared FEMA/DHS and NRC packets, but left state/local routes as triage-needed. That was too risky because the public record trail may be split across FEMA, PEMA, Beaver County, Ohio EMA, and Columbiana County.

The most important new finding is a capture fork. Local reporting says a FEMA representative would announce the results of the biennial exercise at the Columbiana County EMA office in Lisbon at 11:00 Friday, while FEMA would later discuss IPAWS at 17:30. This means a single 17:30 meeting watch is not enough. The cube now treats the 11:00 local results announcement as a separate acquisition target, not as proof.

## Priority changes made

- Built PEMA RTKL request packet: `records-requests/bvps-rev0374/rrt-0374-003-pema-rtkl-ans-exercise-afn-capa.md`.
- Built Beaver County open-records packet: `records-requests/bvps-rev0374/rrt-0374-004-beaver-county-open-records-warning-afn-local-logs.md`.
- Built Ohio EMA / Columbiana County packet: `records-requests/bvps-rev0374/rrt-0374-005-ohio-ema-columbiana-bvps-exercise-records.md`.
- Added `cube/bvps-records-dispatch-triage-rev0374.csv` so all P0/P1 federal/state/local packets are now in ready-not-sent form.
- Added `cube/bvps-proofcut-minimum-evidence-thresholds-rev0374.csv` to define what would actually count for meeting, ANS/IPAWS, EOF, AFN, CAP, and chain-of-custody proofcuts.
- Added `cube/bvps-evidence-adjudication-workbench-rev0374.csv` so incoming packets can be mapped to proofcuts without overcrediting.
- Added `cube/bvps-dlp-redaction-intake-gate-rev0374.csv` and `evidence-intake/bvps-response-sidecar-template-rev0374.csv` so sensitive personal/security material is handled before any public release.
- Built `evidence-bags/bvps-dispatch-intake-capsule-rev0374.zip` as the compact active workset for dispatch and response intake.

## Audit/refactor performed

Rev0374 adds a concrete audit of root-vs-cube validation-report mirrors: `cube/validation-report-mirror-audit-rev0374.csv`. The package currently has many duplicate validation report mirrors; exact duplicates should eventually collapse to a single referenced copy, while divergent pairs must remain until reviewed. This is not allowed to distract from evidence acquisition, so the refactor output is a compact dispatch/intake capsule rather than a full destructive prune.

The source graph is extended and resynchronized through S1377. New sources are route/context or open-source acquisition targets only. They cannot close readiness proofcuts.

## Non-claims

- No real Beaver Valley response packet has been imported.
- No records request has been sent from this static archive.
- No official preliminary-findings packet has been adjudicated.
- No ANS/IPAWS transition proofcut is closed.
- No EN58200 EOF repair/retest/corrective-action proofcut is closed.
- No local readiness conclusion is made.


# 580 — Nuclear emergency preparedness: meeting watch, source graph repair, records-route reverification, and active-surface refactor

Revision: rev0373  
Base: rev0372  
Status: canon  
Claim posture: capture-ready / route-reverified / dispatch-ready / public-meeting-watch-open / source-graph-synced / active-surface-capsule-built / EOF-LER-watch-open / ANS-transition-gate-open / claim-frozen / no local readiness conclusion

## Substance-first changes

This revision focuses on the work most at risk of being missed rather than adding another layer of doctrine. The riskiest gap is the June 12, 2026 Beaver Valley public-meeting evidence window: if preliminary findings, ANS statements, slides, Q&A, or meeting materials are not captured while the trail is fresh, the cube will be forced to rely on stale notices and route pages. Rev0373 therefore converts the issue into an acquisition queue with ready request packets and explicit non-claim rules.

The second concrete risk is the March 2026 EOF power-loss follow-up. EN58200 remains a trigger only: compensatory measures and an event notice do not prove repair, retest, or readiness. Rev0373 creates the NRC ADAMS/FOIA request packet that asks for reportability, LER/corrective-action, restoration/retest, and future FEMA transmittal accessions.

The third risk was an internal integrity failure in the source graph. Rev0372 correctly noticed S1356-S1358 were missing from the source-use ledger, but a deeper graph scan found more drift: S1359-S1364 were absent from the markdown register, and index rows already referenced S1365-S1371 even though those IDs were absent from the canonical source table. Rev0373 repairs that graph instead of just documenting it.

## New high-priority acquisition controls

- `cube/bvps-public-meeting-acquisition-status-rev0373.csv` keeps the public-meeting packet, ANS disposition, FEMA transmittal, final-report watch, and EOF follow-up open.
- `cube/bvps-records-route-reverification-rev0373.csv` records current FEMA/DHS, NRC, Pennsylvania, Beaver County, Ohio EMA, and trigger routes.
- `cube/bvps-records-dispatch-triage-rev0373.csv` prioritizes the next request sequence.
- `records-requests/bvps-rev0373/rrt-0373-001-fema-region-3-online-foia-public-meeting-followup.md` is ready text for FEMA/DHS.
- `records-requests/bvps-rev0373/rrt-0373-002-nrc-adams-foia-eof-ler-fema-transmittal-followup.md` is ready text for NRC.
- `records-requests/bvps-rev0373/immediate-dispatch-order-rev0373.md` states the operational sequence and logging requirements.

No request has been sent by this static archive. Template creation is not dispatch proof.

## Source graph refactor

Rev0373 makes source provenance mechanically consistent again:

- `cube/source.csv` now contains S1365-S1371.
- `sources/register.md` now contains S1359-S1371.
- `cube/source-use-ledger.csv` was recomputed from `cube/index.csv` instead of patched by hand.
- `cube/source-edge-table.csv` was regenerated from index source IDs.
- `cube/file-source-edge.csv` was backfilled for missing index edges while preserving historical metadata.
- `cube/source-graph-sync-audit-rev0373.csv` records before/after controls.

This is package integrity only. Source registration, route verification, and alias collapse do not establish BVPS readiness.

## Active-surface refactor

The package still carries useful historical luggage, but full-cube scans are wasteful for the active BVPS acquisition problem. Rev0373 builds a compact active-surface manifest and capsule:

- `cube/bvps-active-surface-manifest-rev0373.csv`
- `evidence-bags/bvps-active-surface-capsule-rev0373.zip`

The active surface contains the current front doors, route/request controls, source graph, key existing BVPS proofcut/hotpath files, and validators. It is meant to be the default work surface for the next session. Historical matrices and older SQLite mirrors remain in the package but no longer need to be dragged through every check.

## Speculative posture

The likely failure mode is not a false positive from one bad document; it is slow evidence decay. Meeting material can disappear into non-indexed agency workflows, local ANS/AFN details can be compressed into high-level federal language, and the EOF power-loss follow-up can become invisible unless ADAMS/FOIA routing is started now. The package should therefore treat dispatch receipts and response packets as first-class evidence objects in the next revision.

## Non-claims

- No real Beaver Valley exercise response packet has been imported.
- No records request has been sent from this static archive.
- No public-meeting preliminary finding has been adjudicated.
- No ANS transition proofcut is closed.
- No EOF repair/retest/corrective-action proofcut is closed.
- No local readiness conclusion is made.

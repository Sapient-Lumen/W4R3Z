# Structural audit — rev0277

Date: 2026-05-23 00:50 America/New_York  
Archive focus: query views, dashboards, observability, rumor control, OT / SCADA safety, Natech / toxic legacy, climate-sensitive disease surveillance, and contestable public ledgers.

## What this pass found

rev0276 successfully made service floors scoreable, owned, freshness-aware, fiscal / market-aware, border-aware, basin-aware, and informal-user-aware. The next defect was operability: the cube could state readiness attributes but still lacked enough first-class machinery to ask recurring questions, publish public status safely, detect false precision, control rumor, protect cyber-physical controls, see toxic legacy sites, detect climate-sensitive disease early, and let affected people challenge wrong data.

Two structural defects were also repaired:

1. `cube/schema.json` still declared `rev0275` and contained a duplicate rev0276 note.
2. `cube/service-floor-checklist.csv` had malformed scarcity-priority rows with inconsistent column counts.

## Changes made

- Added files `364`–`371`.
- Added observability and contestability fields to `cube/schema.json` and `cube/index.csv`.
- Added four operational CSVs:
  - `query-view-catalog.csv`
  - `dashboard-and-telemetry-register.csv`
  - `natech-toxic-legacy-register.csv`
  - `health-surveillance-readiness.csv`
- Repaired `service-floor-checklist.csv` and added rev0277 checklist rows.
- Extended `interdependency-matrix.csv` and `scenario-loadcase-library.csv`.
- Added sources `S653`–`S667`.
- Added open questions `117`–`124`.

## Structural rule added

No future service-floor packet should score above R2 unless it can be observed through a maintained dashboard, ledger, or tested manual reporting path. No packet should score above R3 unless affected users can challenge wrong status, unsafe clearance, exclusion, or stale data and see correction status.

## Next likely gaps

The cube is now ready for a sample-jurisdiction phase: populate the schema with a fictional or real locality, score five service floors under two loadcases, and test whether the query views produce actionable gaps. Future substantive gaps remain, but rev0278 should probably create a **worked example** before admitting another large stack of canon notes.

---
Citations point to `sources/register.md`.

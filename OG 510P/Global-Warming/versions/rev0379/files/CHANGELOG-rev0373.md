
# Changelog rev0373

- Added `580-nuclear-emergency-preparedness-meetingwatch-sourcegraph-activesurface-refactor-compact-canon.md` as the rev0373 front door.
- Reverified current records/acquisition routes and separated route context from evidence.
- Added FEMA/DHS and NRC request packets under `records-requests/bvps-rev0373/`.
- Added public-meeting acquisition status and records-dispatch triage tables.
- Added S1365-S1371 to `cube/source.csv` and S1359-S1371 to `sources/register.md` where missing.
- Recomputed `cube/source-use-ledger.csv` and regenerated `cube/source-edge-table.csv` from `cube/index.csv`.
- Backfilled `cube/file-source-edge.csv` missing index edges while preserving old metadata.
- Added `cube/source-canonical-url-map-rev0373.csv` and `cube/source-canonical-cluster-summary-rev0373.csv`.
- Added `cube/source-graph-sync-audit-rev0373.csv`.
- Added compact active-surface manifest and capsule.
- Added rev0373 validators for source graph sync, public-meeting acquisition, route reverification, active-surface capsule, manifest/schema sync, tool compile, and validation-report status vocabulary.
- Preserved no-readiness-conclusion posture.

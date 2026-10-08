# CHANGELOG rev0309

Created: 2026-06-04T04:31:00-04:00

## Added

- Added file 516: emergency preparedness site localization, readiness scoring, and change-control spine.
- Added four synthetic site fixtures and fourteen synthetic offsite-jurisdiction fixtures.
- Expanded the 264 rev0308 local evidence slots across four fixtures into 1,056 sample evidence rows.
- Added site/floor readiness scoring, critical gap summaries, and a gap burn-down queue.
- Added synthetic exercise-result rows from the rev0308 inject runbook.
- Added 10 CFR 50.54(q)-style emergency-plan change/effectiveness review fixtures.
- Added 10 CFR 50.160 performance-objective metrics for the advanced-reactor branch.
- Added a rev0309 emergency-focused SQLite mirror plus resource map.

## Refactor / audit

- Kept legacy universal crossproduct tables for compatibility but routed emergency-readiness queries to the sparse/local/scoring chain.
- Updated source, route, tag, file, file-core, index, query-view, schema, source-use, table-catalog, and resource-manifest surfaces.
- Added source freshness, cloudtainer hygiene, risk burn-up, and refactor backlog rows.

## Warning

The fixture rows are synthetic and are not evidence of real nuclear-site readiness.

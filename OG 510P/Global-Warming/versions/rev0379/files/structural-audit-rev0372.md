# Structural audit rev0372

## Scope

Deep read of the rev0371 cloudtainer, with online context checks for the active Beaver Valley nuclear-emergency-preparedness branch and for the broader global-warming doctrine layer.

## High-signal findings

- The package contains 5,378 files and 383,563,702 unpacked bytes before this revision. `cube/` accounts for 373,534,721 bytes.
- Current rev0371 validation is materially conservative: active checks pass while real-evidence and records-response gates remain pending.
- A package-wide tool syntax scan failed before repair because two historical validators had broken newline string literals.
- The package identity layer had stale copies: `cube/manifest.json` lagged at rev0369 and both schema files lagged at rev0368.
- Source registration has useful alias rules, but `cube/source-use-ledger.csv` is stale for `S1356`, `S1357`, and `S1358`.
- The largest waste sources are historical matrices, SQLite mirror sprawl, and exact duplicate clusters. These should be externalized or moved behind an explicit historical-luggage path, not deleted blindly.

## Corrective actions in rev0372

- Repaired the broken historical validators.
- Added package-wide syntax validation.
- Synchronized root/cube manifest, schema, and validation-rules identity to rev0372.
- Added audits for cloudtainer deep-read metrics, waste burn-down targets, source ledger sync debt, and resource-manifest delta.

## Deferred

- No real BVPS exercise evidence packet was created or imported.
- No records requests were sent by this static archive.
- No source-edge/ledger backfill was synthesized by hand.
- No destructive removal of historical matrices, duplicate files, or SQLite mirrors was performed.
- The hotpath SQLite/capsule was not rebuilt because the revision is a package-hygiene correction, not a new evidence-acquisition surface.

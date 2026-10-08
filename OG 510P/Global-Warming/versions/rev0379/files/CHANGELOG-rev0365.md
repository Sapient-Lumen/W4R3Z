# CHANGELOG rev0365

## Added

- Added `572-nuclear-emergency-preparedness-chaincustody-intakecli-fieldkitpointers-refactor-compact-canon.md` as the rev0365 front-door canon.
- Added an evidence packet contract for the highest-risk BVPS artifact classes.
- Added a chain-of-custody intake ledger whose real-evidence rows remain explicitly awaiting packet arrival.
- Added a hashing intake CLI and a safe fixture drop proving the executable path.
- Added a no-readiness-overclaim scanner for current-risk files.
- Added a pointer-based BVPS rev0365 field kit to stop adding duplicate convenience copies.
- Added rev0365 validation report and current-risk validator sweep.

## Changed

- Updated README, manifests, schema files, resource manifest, table-column catalog, and index/file/file-core rows to rev0365.
- Kept source IDs stable; repeat online context checks are recorded as source-review events rather than new duplicate source IDs.

## Not changed

- No real BVPS exercise evidence packet has been imported.
- No local readiness, unreadiness, exercise success, or alert effectiveness claim is made.
- Historical field-kit duplicates, SQLite mirrors, and giant matrices remain available pending a separate compaction boundary.

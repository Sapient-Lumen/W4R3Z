# DeriveBSD rev0563 session review

## Focus

This pass stayed on the real FreeBSD host-proof receive/import path and targeted the next risky seam after nofollow source copying: durable evidence that remains auditable after the original handoff directory, sealed archive scratch directory, or removable-media source is gone.

## Material changes

- Bumped the cube cut to `2026-06-16r592`.
- Added canonical `copied_handoff_snapshot` evidence to `import.receipt.json`, including copied member paths, sizes, SHA-256 digests, total bytes, file count, and a canonical manifest digest.
- Added durable write/publish evidence to import receipts via `durable_write_policy` and an fsync-aware `atomic_publish_policy`.
- Hardened the importer implementation so copied handoff files, import receipts, staging directories, and import parent directories are fsynced around the atomic full-digest publish path.
- Extended the import auditor to recompute and reject missing or tampered copied-snapshot manifests, stale durable policies, and stale publish-policy text.
- Extended the loose importer, sealed importer, and import-audit release-critical checks so the new copied snapshot and durable publish invariants are executable regressions rather than doctrine.
- Refreshed host-smoke fixtures, proof-bundle fixtures, generated catalogs, schema audit artifacts, refactor backlog artifacts, hygiene checkset artifacts, generated docs, current operator-facing docs, and the release-critical run ledger.

## Validation

- `release-critical`: 48 / 48 passed.
- `schema-cube-audit`: 3 / 3 passed.
- `validate_spec_examples.py`: 469 examples validated.
- Strict duplicate-key scan: 1426 JSON files scanned.
- Generated docs and generated artifact release IDs passed.
- Final Python bytecode artifact check passed.

## Remaining risk

This is still a Linux cloudtainer pass. It materially improves durability and auditability of the FreeBSD host-proof import path, but it does not include a non-simulated FreeBSD `real-host-proof` import. The next highest-value action remains producing a real sealed FreeBSD handoff on a host and importing it through the one-command sealed importer.

# DeriveBSD rev0562 session review: nofollow copy snapshot

## Focus

This pass targeted the next high-risk gap in the real FreeBSD host-proof receive path: loose directory imports still read from mutable source handoff directories. A verifier-before-copy model can be bypassed by later source mutation unless the importer itself treats the source as hostile, copies a bounded snapshot without following symlinks, and re-verifies the staged copy before publishing.

## Changes

- Hardened `tools/freebsd/import_removable_media_local_fallback_host_proof_handoff.py` so direct directory imports copy only the allowed proof members through a directory file descriptor and nofollow-capable open flags where available.
- Added bounded, exclusive staging writes for copied proof members, with regular-file revalidation, finite member-size enforcement, fsync, and normalized permissions before publish.
- Changed direct loose-handoff provenance so `source_transport.sha256sums_byte_sha256` is computed from the copied staged handoff snapshot, not from the still-mutable source path.
- Added `DIRECTORY_IMPORT_COPY_POLICY` to `tools/freebsd/host_proof_contract.py` and bound it into both direct imports and sealed imports.
- Extended import receipts with `copy_policy` and invariants proving that directory imports copy allowed regular files without following symlinks and bind the copied snapshot rather than a mutable source.
- Extended the import-root auditor to reject missing or stale nofollow staging-copy policy evidence.
- Added release-critical regression coverage for allowed-name symlink members, missing copy policy, and sealed-import propagation of the directory import copy contract.
- Refreshed host-smoke fixtures, proof-bundle fixtures, generated catalogs, schema audit artifacts, refactor backlog artifacts, current operator docs, and the release-critical ledger for `2026-06-16r591`.
- Compacted front-door release text instead of raising the front-door budget.

## Validation

- `release-critical`: 48 / 48 passed.
- `schema-cube-audit`: 3 / 3 passed.
- `validate_spec_examples.py`: 469 examples validated.
- Generated docs and generated artifact release-id checks passed.
- Front-door budget check passed.
- Python bytecode artifact check passed after cleanup.
- ZIP integrity check passed for the packaged revision.

## Remaining risk

This remains a Linux cloudtainer pass. It hardens the loose and sealed host-proof import paths, but it still does not include a non-simulated FreeBSD `real-host-proof` import.

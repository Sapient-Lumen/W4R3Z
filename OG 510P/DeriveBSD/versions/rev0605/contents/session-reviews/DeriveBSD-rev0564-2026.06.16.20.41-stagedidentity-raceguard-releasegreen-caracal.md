# DeriveBSD rev0564 session review

## Focus

This pass stayed on the risky FreeBSD host-proof import boundary. The prior importer was durable after copy, but it still computed the final digest-named import directory from source JSON read before the copy boundary. Because loose removable-media handoff directories are mutable, a source could change between pre-verification and copy and leave the published import identity describing a receipt different from the copied proof bytes.

## Concrete changes

- Bumped the cube cut to `2026-06-16r593`.
- Added `IMPORT_STAGED_IDENTITY_POLICY` in `tools/freebsd/host_proof_contract.py`.
- Refactored `tools/freebsd/import_removable_media_local_fallback_host_proof_handoff.py` so final import identity is computed only after the copied handoff snapshot is reverified.
- The importer now reloads `receipt.json` and `bundle.json` from the copied staging snapshot before computing `contract.import_directory_name(...)` and before writing `import.receipt.json` summaries.
- `import.receipt.json` now records `identity_policy` and asserts:
  - `import_directory_identity_derived_from_reverified_copied_snapshot`
  - `import_receipt_summaries_loaded_from_reverified_copied_snapshot`
- Extended `tools/freebsd/audit_removable_media_local_fallback_host_proof_imports.py` to reject missing staged snapshot identity policy evidence.
- Extended `tools/check_removable_media_local_fallback_freebsd_host_proof_importer.py` with a source-flip regression: the check simulates a handoff changing between pre-verify and copy, and requires the imported directory to follow the copied receipt canonical digest rather than the original source digest.
- Refreshed host-smoke/proof-bundle examples, generated docs, schema audit/refactor/checkset artifacts, front-door docs, and release ledgers for `2026-06-16r593`.

## Why it matters

This closes a subtle evidence-identity race. The importer already copied through nofollow staging and wrote durable snapshot manifests, but the final directory name still came from the mutable source before the copy. Now the import name, receipt summaries, copied snapshot manifest, source transport, and audit all agree on the bytes that were actually staged and published.

## Validation

- `release-critical`: 48 / 48 passed.
- `schema-cube-audit`: 3 / 3 passed.
- `validate_spec_examples.py`: 469 examples validated.
- Strict duplicate-key scan: 1426 JSON files scanned.
- Generated docs and generated artifact version checks passed.
- Python bytecode artifact check passed.
- Python executable-bit check passed.

## Remaining caveat

This remains a Linux cloudtainer pass. It hardens the real FreeBSD proof import path, but it still does not include a non-simulated FreeBSD `real-host-proof` import.

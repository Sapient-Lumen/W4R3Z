# DeriveBSD-rev0554-2026.06.16.15.54-exactrunreceipt-proofclaimguard-releasegreen-ibis

## Focus

This pass stayed on the scarce real FreeBSD host-proof path and tightened a recovery-evidence seam instead of adding another doctrine or registry surface. The target risk was that a collect/import run receipt could be valid JSON and stage-consistent while still carrying stray fields, misleading invariant claims, or an accidental `proof_status = real-host-proof` marker.

## Changes

- Tightened `tools/freebsd/validate_collect_import_run_receipt.py` so strict collect/import run receipts must match an exact top-level key set and exact invariant key set.
- Added banned proof-claim key detection for `proof_status`, preventing recovery receipts from carrying standalone real-proof claims.
- Refactored `tools/freebsd/write_collect_import_run_receipt.py` to emit `run_receipt_exact_key_set_enforced` and continue self-validating before atomic symlink-refusing publish.
- Extended `tools/check_removable_media_local_fallback_freebsd_host_proof_collect_import.py` so release-critical rejects tampered receipts that add `proof_status = real-host-proof` or unexpected invariant keys, while retaining the existing one-command collect → verify → import → audit guard.
- Kept the FreeBSD proof-tool digest set at exactly 14 rows; this is a proof-path hardening/refactor pass, not a new proof family.
- Refreshed host-smoke/proof-bundle examples, generated docs/catalogs, cube audit/checkset/backlog artifacts, the canonical hygiene ledger, current front doors, and this session review for `2026-06-16r584`.

## Validation

- `release-critical`: 45 / 45 passed.
- `schema-cube-audit`: 3 / 3 passed.
- `check_json_duplicate_key_rejection.py`: strict scan passed before packaging.
- `check_generated_docs.py`: clean.
- `check_no_python_bytecode_artifacts.py`: clean before archive creation.

## Boundary

This revision still does not contain a non-simulated FreeBSD host receipt or production `real-host-proof` import. The checked proof bundle remains explicit non-proof simulation material until a supported real FreeBSD host run is collected, verified, imported, and audited.

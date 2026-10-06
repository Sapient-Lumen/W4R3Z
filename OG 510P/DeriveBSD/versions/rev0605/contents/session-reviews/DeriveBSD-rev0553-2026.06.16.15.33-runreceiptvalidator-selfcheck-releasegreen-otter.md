# DeriveBSD-rev0553-2026.06.16.15.33-runreceiptvalidator-selfcheck-releasegreen-otter

## Focus

This pass stayed on the scarce real-host proof path and avoided a new registry family. The target risk was run-receipt trust: rev0552 made run-receipt writes atomic and symlink-refusing, but the receipt shape itself was still only indirectly checked by the collect/import release guard.

## Changes

- Added `tools/freebsd/validate_collect_import_run_receipt.py`, a standalone strict validator for `removable.media.local.freebsd.host.proof.collect_import.run.receipt`.
- Refactored `tools/freebsd/write_collect_import_run_receipt.py` so the writer self-validates the payload before atomic publish.
- Extended `tools/check_removable_media_local_fallback_freebsd_host_proof_collect_import.py` to run the standalone validator against an emitted failed-resume receipt and reject a tampered receipt that falsely reports `collect` during resume.
- Updated `tools/freebsd/preflight_removable_media_local_fallback_host_proof.sh` to require and import-check the run-receipt validator before scarce host work.
- Bound the validator into `tools/freebsd/host_proof_contract.py`; proof bundles now bind exactly 14 FreeBSD proof-tool digest rows.
- Refreshed host-smoke/proof-bundle examples, generated docs/catalogs, cube audit/checkset/backlog artifacts, the canonical hygiene ledger, current front doors, and this session review for `2026-06-16r583`.

## Validation

- `release-critical`: 45 / 45 passed.
- `schema-cube-audit`: 3 / 3 passed.
- `check_json_duplicate_key_rejection.py`: 1419 JSON files scanned.
- `check_no_python_bytecode_artifacts.py`: clean.
- `check_generated_docs.py`: clean.

## Boundary

This revision still does not contain a non-simulated FreeBSD host receipt. The checked proof bundle remains explicit non-proof simulation material until a supported real FreeBSD host run is collected, verified, imported, and audited.

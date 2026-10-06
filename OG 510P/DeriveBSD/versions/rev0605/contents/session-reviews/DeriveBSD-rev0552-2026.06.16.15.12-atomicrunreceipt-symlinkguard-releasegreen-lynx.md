# DeriveBSD rev0552 session review — atomic run-receipt writer and symlink guard

## Mission risk attacked

The real FreeBSD proof path had gained a strict one-shot collect/import/audit wrapper and a machine-readable run receipt, but the receipt was still built inline inside the shell wrapper and written directly to the requested path. That made the next scarce-run risk concrete: a root-running proof attempt could lose or redirect failure evidence if the receipt path was hostile, symlinked, or only partially written.

## Changes made

- Added `tools/freebsd/write_collect_import_run_receipt.py` as the bound run-receipt writer.
- Refactored `tools/freebsd/collect_import_removable_media_local_fallback_host_proof.sh` so the exit trap delegates JSON construction to the writer instead of embedding Python in the shell script.
- The writer validates stage-order prefixes, records `run_receipt_write_policy = atomic-tempfile-fsync-osreplace-symlink-destination-refused`, writes through an O_EXCL same-directory temporary file, fsyncs, publishes with `os.replace`, and refuses symlink receipt destinations.
- Hardened wrapper cleanup so a requested run-receipt write failure cannot make an otherwise green auto-created handoff disappear silently; the handoff is preserved when receipt evidence cannot be written.
- Extended `tools/check_removable_media_local_fallback_freebsd_host_proof_collect_import.py` to prove missing-handoff resume still records `verify_handoff`, proves collection is not rerun, and proves a symlink run-receipt destination does not overwrite its target.
- Added the run-receipt writer to `tools/freebsd/host_proof_contract.py`; proof bundles now bind exactly 13 FreeBSD proof-tool digest rows.
- Updated preflight, host-smoke/proof-bundle examples, generated catalogs, cube audit/backlog/checkset artifacts, current front doors, and hygiene ledgers for `2026-06-16r582`.

## Audit/refactor note

This was a real refactor, not a new registry family: the brittle inline receipt JSON writer moved out of the shell into a dedicated Python tool, while the existing release-critical collect/import checker was strengthened instead of adding another proof-family checker. The documentation front door was also trimmed to stay within the existing budget ratchet.

## Validation

- `release-critical`: 45 / 45 passed.
- `schema-cube-audit`: 3 / 3 passed.
- Strict JSON duplicate-key scan: 1416 JSON files scanned.
- No Python bytecode artifacts remained before packaging.
- The checked proof bundle remains `checker-simulation-non-proof`; no real FreeBSD host proof is claimed.

## Next highest-value step

Run `tools/freebsd/collect_import_removable_media_local_fallback_host_proof.sh --run-receipt /path/to/run.receipt.json` on a supported real FreeBSD host. If collection succeeds but import/audit fails, preserve the handoff and resume with `--resume-handoff HANDOFF_DIR`; the run receipt should now name the failing stage without writing through symlink destinations.

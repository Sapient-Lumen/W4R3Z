# DeriveBSD rev0559 session review — full-digest imports and atomic unseal publish

Target archive filename: `DeriveBSD-rev0559-2026.06.16.18.27-fulldigest-atomicpublish-releasegreen-panther.zip`.

## Priority chosen

The riskiest unfinished work remains the scarce, non-simulated FreeBSD `real-host-proof` import. This pass therefore stayed on the proof handoff/import path and looked for ways a real proof handoff could still be confused, clobbered, or made hard to diagnose before the cloudtainer import/audit step.

## Substantive changes

- Bumped the cube cut to `2026-06-16r588` after changing the host-proof contract.
- Hardened `tools/freebsd/verify_removable_media_local_fallback_host_proof_handoff.py` so allowed handoff member names are checked by directory membership first, then symlink refusal, then regular-file validation. Broken `receipt.json`, `bundle.json`, `SHA256SUMS`, or optional `README.import.txt` symlinks now fail as typed verifier errors instead of being ignored or surfacing as traceback-shaped failures.
- Refactored proof-import directory naming into `tools/freebsd/host_proof_contract.py` with `import_directory_name(...)`, `IMPORT_DIRECTORY_DIGEST_HEX_LENGTH`, and `IMPORT_DIRECTORY_DIGEST_POLICY`.
- Hardened `tools/freebsd/import_removable_media_local_fallback_host_proof_handoff.py` so final import directories bind proof status plus the full 64-hex receipt canonical SHA-256 instead of a short 16-hex prefix.
- Updated `tools/freebsd/audit_removable_media_local_fallback_host_proof_imports.py` to recompute and require the same full-digest import directory name during root audit.
- Hardened `tools/freebsd/unseal_removable_media_local_fallback_host_proof_handoff.py` replacement publish: verified staging is now atomically moved through a temporary sibling backup, stale replacement-backup residue is refused, and the old output is not removed before the new handoff is ready.

## Audit/refactor work

- Extended release-critical importer and import-audit checks to prove full receipt canonical digest naming and reject a legacy short-prefix import directory.
- Extended handoff verifier checks to prove broken required and optional symlink members are operator-shaped errors, not crashes or silent skips.
- Extended handoff seal/unseal checks to prove atomic replacement leaves no backup residue and refuses stale backup siblings.
- Rebuilt the host-smoke simulation and proof bundle for `2026-06-16r588` rather than preserving stale `r587` fixtures.
- Regenerated schema audit, refactor backlog, hygiene checkset, generated catalog, artifact indexes, and the release-critical run ledger.
- Fixed release-front-door sediment caught by the full ledger: restored the missing `2026-06-16r587` changelog/index heading and compacted front-door index lines instead of raising the budget.

## Validation

- `tools/hygiene.py --profile release-critical`: 47 / 47 passed, recorded in `spec/examples/cube.hygiene.run.ledger.json`.
- `tools/hygiene.py --profile schema-cube-audit`: 3 / 3 passed.
- `tools/validate_spec_examples.py`: 469 examples validated.
- `tools/check_generated_docs.py`: passed after regenerating `docs/_generated/doc_catalog.json`.
- `tools/check_cube_hygiene_run_ledger.py`: passed against the final completed release-critical ledger.
- `tools/check_no_python_bytecode_artifacts.py`: passed after cleanup.
- ZIP integrity and archive SHA-256 were checked after packaging.

## Caveat

This remains a Linux cloudtainer pass. It materially hardens proof handoff verification, import identity, and unseal replacement, but it still does not contain a non-simulated FreeBSD `real-host-proof` import.

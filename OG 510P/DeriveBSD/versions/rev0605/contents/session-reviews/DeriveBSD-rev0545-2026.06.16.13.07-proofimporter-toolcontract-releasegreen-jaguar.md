# DeriveBSD rev0545 session review — proof importer and tool contract

This pass continued the risk-first FreeBSD removable-media proof lane without adding another doctrine/registry surface. The concrete gap after rev0544 was that a verified handoff still had to be copied into the cube by convention. Rev0545 adds a finite importer, hardens the handoff verifier, and refactors the proof-tool set into one shared contract so the finalizer, validator, verifier, importer, and release-critical checks cannot silently disagree.

## Substantive changes

- Added `tools/freebsd/import_removable_media_local_fallback_host_proof_handoff.py`. Default import runs strict handoff verification first, accepts only real host proof, creates a digest-named import directory, preserves the verified package under `handoff/`, and writes `import.receipt.json` beside it.
- Added `tools/check_removable_media_local_fallback_freebsd_host_proof_importer.py` and wired it into release-critical. The checker proves default rejection of checker simulations, explicit non-proof import labeling, copied-handoff reverification, duplicate import refusal, and deliberate `--replace` behavior.
- Added `tools/freebsd/host_proof_contract.py` to centralize the current cube cut, runner contract, FreeBSD release floor, handoff filenames, and exact proof-tool path set.
- Updated proof bundles to bind exactly 9 proof-tool digest rows: the contract module, collector, runner, receipt validator, finalizer, bundle validator, handoff verifier, handoff importer, and C worker source.
- Hardened the handoff verifier so optional `README.import.txt` cannot be a symlink or non-regular file.

## Audit/refactor notes

The refactor removed a drift-prone duplication point: the finalizer, bundle validator, proof-bundle checker, handoff verifier, and importer now share the host-proof contract instead of carrying separate proof-tool path and version constants. The schema surface changed only where it reflected executable proof reality: the proof bundle tool digest array moved from 6 to 9 rows.

## Validation

- `release-critical`: passed 41 / 41.
- `schema-cube-audit`: passed 3 / 3.
- strict JSON duplicate-key scan is included in release-critical and passed after the session artifacts were added.
- No non-simulated FreeBSD host proof is claimed in this revision.

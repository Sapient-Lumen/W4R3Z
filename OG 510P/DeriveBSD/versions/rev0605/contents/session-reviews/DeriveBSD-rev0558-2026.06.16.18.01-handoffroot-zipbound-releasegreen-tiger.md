# DeriveBSD rev0558 session review — handoff root and ZIP bounds

Target archive filename: `DeriveBSD-rev0558-2026.06.16.18.01-handoffroot-zipbound-releasegreen-tiger.zip`.

## Priority chosen

The riskiest unfinished work remains the scarce, non-simulated FreeBSD `real-host-proof` import. This pass therefore stayed on the proof handoff path and avoided broad new registry or doctrine surface. The main question was whether a real host handoff could still be corrupted, confused, or unsafe before import.

## Substantive changes

- Bumped the cube cut to `2026-06-16r587` after changing the host-proof contract.
- Hardened `tools/freebsd/verify_removable_media_local_fallback_host_proof_handoff.py` so the handoff directory itself must not be a symlink, not just the member files below it.
- Hardened `tools/freebsd/seal_removable_media_local_fallback_host_proof_handoff.py` so the input handoff root is checked before resolution and cannot be a symlinked directory source.
- Hardened `tools/freebsd/import_removable_media_local_fallback_host_proof_handoff.py` so both the handoff source and import root are checked before resolution/copying, closing another symlink-source confusion path.
- Hardened `tools/freebsd/unseal_removable_media_local_fallback_host_proof_handoff.py` so sealed transport archives must be deterministic and bounded: stored entries only, fixed timestamps, normalized regular-file modes, finite archive/member/total payload limits, duplicate-name rejection, unsafe-name rejection, encrypted-entry rejection, streamed extraction, byte-count checking, exclusive creation, and `O_NOFOLLOW` where available.
- Extended the release-critical handoff, sealer, and importer checks to prove symlinked handoff-root refusal and compressed archive rejection.

## Audit/refactor work

- Refactored deterministic handoff archive format, fixed ZIP timestamp/mode, and finite size limits into `tools/freebsd/host_proof_contract.py` instead of keeping those literals scattered across transport tools and checkers.
- Regenerated host-smoke and proof-bundle examples against the new `2026-06-16r587` cube-cut contract rather than preserving stale receipts.
- Regenerated cube schema audit, refactor backlog, hygiene checkset, generated docs, and artifact indexes after the cut bump.
- Fixed stale current-doc proof-tool count drift caught during audit: operator-facing docs are now checked against the contract instead of trusted by prose.
- Rebuilt the release-critical run ledger in resumable chunks after validation exposed stale generated discovery/front-door surfaces and bytecode residue from earlier imports.

## Validation

- `tools/hygiene.py --profile release-critical`: 47 / 47 passed, recorded in `spec/examples/cube.hygiene.run.ledger.json`.
- `tools/hygiene.py --profile schema-cube-audit`: 3 / 3 passed.
- `tools/validate_spec_examples.py`: 469 examples validated.
- `tools/check_generated_docs.py`: passed after regenerating `docs/_generated/doc_catalog.json`.
- `tools/check_no_python_bytecode_artifacts.py`: passed after cleanup.
- ZIP integrity and archive SHA-256 were checked after packaging.

## Caveat

This remains a Linux cloudtainer pass. It materially reduces transport and import confusion around the scarce FreeBSD proof path, but it still does not contain a non-simulated FreeBSD `real-host-proof` import.

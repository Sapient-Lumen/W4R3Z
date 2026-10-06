# DeriveBSD rev0557 session review — handoff seal/unseal and symlink guard

Target archive filename: `DeriveBSD-rev0557-2026.06.16.17.39-handoffseal-symlinkguard-releasegreen-puma.zip`.

## Priority chosen

The riskiest unfinished project work remains the scarce, non-simulated FreeBSD `real-host-proof` import. This session therefore avoided new doctrine/registry surface and worked on the proof handoff path itself: making the finite FreeBSD handoff easier to transport, harder to mix with loose files, and safer to recover in the cloudtainer before import.

## Substantive changes

- Added `tools/freebsd/seal_removable_media_local_fallback_host_proof_handoff.py`, a default-real-proof-only deterministic ZIP sealer for finite handoff directories.
- Added `tools/freebsd/unseal_removable_media_local_fallback_host_proof_handoff.py`, a safe unsealer that rejects unexpected/archive traversal names before extraction, writes into staging, and revalidates before publishing the output directory.
- Added release-critical `tools/check_removable_media_local_fallback_freebsd_host_proof_handoff_seal.py`, which proves deterministic bytes, fixed ZIP timestamps, stored entries, normalized modes, default rejection of checker simulations, refusal of loose handoff files, safe unseal, and path-traversal rejection.
- Fixed a real bug found by the new checker: resolving the sealer output path before final-path symlink checks could overwrite a symlink target. The sealer and unsealer now reject final-path symlinks before resolution.
- Bound the sealer and unsealer into `tools/freebsd/host_proof_contract.py`, raising the proof-tool digest set to exactly 16 rows.
- Updated the real-host operator packet so the preferred scarce-host path is collect finite handoff, optionally seal it as one deterministic archive, and unseal/verify/import/audit in the cloudtainer.
- Updated the FreeBSD preflight surface so the scarce host verifies the sealer and unsealer are present/importable before media authority is used.
- Added stale proof-tool row-count detection to the proof-bundle checker for current operator-facing docs, after finding stale 12/14-row prose drift.
- Regenerated host-smoke/proof-bundle examples for `2026-06-16r586`; proof bundles now contain 16 tool digest rows.

## Audit/refactor work

- Refactored proof-tool path literals into the shared FreeBSD host-proof contract rather than duplicating them in packet/checker surfaces.
- Pruned old `docs/00-index.md` release sediment instead of raising the front-door budget after the new release note exceeded the ratchet.
- Regenerated generated docs and cube audit/checkset/backlog examples after the contract change.
- Rewrote `spec/examples/cube.hygiene.run.ledger.json` as a current partial ledger example so it binds the current wrapper, tool digests, cube input fingerprint, and 47-check release-critical plan without pretending to be a completed run.

## Validation

- `tools/hygiene.py --profile release-critical`: 47 / 47 passed, using a resumable ledger at `/tmp/derivebsd-r586-release.json`.
- `tools/hygiene.py --profile schema-cube-audit`: 3 / 3 passed, using `/tmp/derivebsd-r586-schema.json`.
- `tools/validate_spec_examples.py`: 469 examples validated.
- `tools/check_removable_media_local_fallback_freebsd_host_proof_handoff_seal.py`: passed.
- `tools/check_removable_media_local_fallback_freebsd_host_proof_bundle.py`: passed.
- `tools/check_generated_docs.py`: passed after regenerating `docs/_generated/doc_catalog.json`.
- Python bytecode artifact check passed before packaging.

## Caveat

This remains a Linux cloudtainer pass. It improves the scarce-host handoff path and catches a concrete symlink-overwrite bug, but it still does not import a non-simulated FreeBSD `real-host-proof` receipt.

# DeriveBSD rev0547 session review

Cut: `2026-06-16r577`
Archive stem: `DeriveBSD-rev0547-2026.06.16.13.44-preflight-importroot-releasegreen-falcon`

## Intent

Continue substantive risk reduction on the real FreeBSD removable-media local-fallback proof path without expanding registry doctrine. The target was the next failure point after verified imports: operator scarcity and long-term checked-in import drift.

## Changes

- Added `tools/freebsd/preflight_removable_media_local_fallback_host_proof.sh` so the real-host collector fails before mutable mdconfig/mount work when the host is not FreeBSD, not root, below the supported release floor, missing Capsicum sysctls, or missing required host/proof tools.
- Added `tools/check_removable_media_local_fallback_freebsd_host_proof_preflight.py` to make that preflight a release-critical contract and to prove the cloudtainer refusal path remains non-proof.
- Added `tools/check_removable_media_local_fallback_freebsd_host_proof_checked_import_gate.py` so the checked-in import root `validation/freebsd-host-proof-imports` is audited in default strict mode during release-critical validation.
- Centralized import-root and import-receipt constants in `tools/freebsd/host_proof_contract.py` and bound the preflight script into the FreeBSD proof-tool digest set, now exactly eleven rows.
- Refactored the front-door index to stay within the budget ratchet by routing packet-capture sediment through the generated catalog instead of the human front-door list.

## Validation

- `release-critical`: `44 / 44` passed.
- `schema-cube-audit`: `3 / 3` passed.
- Strict JSON duplicate-key scan passed after the session artifacts were added.
- The theatre gate still finds no strict real-host checked-in bundles and validates checked non-proof simulation material only under explicit non-proof mode.

## Boundary

This cut does not include a non-simulated FreeBSD host receipt. The next real milestone remains a supported FreeBSD host run of `tools/freebsd/collect_removable_media_local_fallback_host_proof.sh` with a verified handoff, importer run, and checked import-root audit.

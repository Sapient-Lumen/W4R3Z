# DeriveBSD-rev0544-2026.06.16.12.52-handoffverify-proofimport-releasegreen-lynx

## Intent

This revision narrows the highest-risk unfinished seam again: the cube still lacks a non-simulated FreeBSD removable-media host receipt, so the handoff/import package must now be finite, checksum-bound, and default-strict before anyone can copy it into the archive as proof.

## Changes

- Added `tools/freebsd/verify_removable_media_local_fallback_host_proof_handoff.py`, a strict handoff verifier for a directory containing only `receipt.json`, `bundle.json`, `SHA256SUMS`, and optional `README.import.txt`.
- Extended `tools/freebsd/collect_removable_media_local_fallback_host_proof.sh` with `DERIVEBSD_HOST_PROOF_HANDOFF_DIR` / third-argument output. The collector now writes the handoff package, emits checksums, invokes the verifier, and still carries no non-proof flags.
- Added `tools/check_removable_media_local_fallback_freebsd_host_proof_handoff.py` and wired it into `release-critical`, raising the bounded profile to 40 checks. It exercises checksum tamper, path-traversal checksum names, unexpected loose files, and default rejection of checker simulations.
- Refactored the proof-bundle validator surface by removing an unreachable duplicate return instead of adding another registry layer.
- Regenerated host-smoke receipts, proof-bundle examples, cube audit/backlog/checkset/ledger artifacts, generated docs/catalogs, and front-door current docs for `2026-06-16r574`.
- Kept `docs/00-index.md` under its front-door budget while still naming the changed front door in the newest release section.

## Validation

- `release-critical`: 40/40 passed.
- `schema-cube-audit`: 3/3 passed.
- Strict JSON duplicate-key scan passed after the review artifacts were added.
- Zip integrity passed after packaging.

## Not claimed

This revision still does not contain a non-simulated FreeBSD host receipt or production `real-host-proof` import. The next real milestone remains running `tools/freebsd/collect_removable_media_local_fallback_host_proof.sh` on a real supported FreeBSD host with `DERIVEBSD_HOST_PROOF_HANDOFF_DIR` set, then importing the resulting finite handoff only after default verification passes.

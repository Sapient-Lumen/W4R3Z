# DeriveBSD rev0538 session review — command-shape and proof-tool strictness

Generated for: `2026-06-12r569`

## Priority risk addressed

The FreeBSD host-proof path already carried command arrays and `command_shape_sha256` fields, but the strict receipt validator only required the digest-shaped field to exist. That left a stale or tampered argv digest able to pass the receipt-level validator. Rev0538 closes that acceptance gap by recomputing every host-probe, media-command, and cleanup `command_shape_sha256` from the canonical argv array during validation.

## Concrete changes

- `tools/freebsd/validate_removable_media_local_fallback_host_smoke_receipt.py` now recomputes and compares command-shape digests with the shared canonical digest helper.
- `tools/freebsd/validate_removable_media_local_fallback_host_proof_bundle.py` now rejects duplicate and unexpected proof-tool rows and requires the exact six-tool set.
- `spec/removable.media.local.freebsd.host.proof.bundle.schema.json` now sets both `minItems` and `maxItems` for the proof-tool digest array.
- Host-smoke and proof-bundle release-critical checks now include tamper regressions for stale command-shape digests, duplicate tool rows, and unexpected tool rows.
- The host-smoke checker reader path now uses the shared duplicate-key rejecting JSON loader.

## Audit/refactor note

This was intentionally not a new registry pass. The audit/refactor was concentrated on the FreeBSD host-proof acceptance seam and its checker family: remove parsing drift, prove the validator rejects stale proof material, and make the future real FreeBSD receipt harder to import incorrectly.

## Open risks

- A real non-simulated FreeBSD host-proof bundle is still absent.
- `docs/00-index.md` remains near its front-door line ceiling even after collapsing a small prose block to keep the r569 note within budget.
- The canonical JSON profile remains the restricted no-float profile, not full arbitrary-number RFC 8785 JCS.

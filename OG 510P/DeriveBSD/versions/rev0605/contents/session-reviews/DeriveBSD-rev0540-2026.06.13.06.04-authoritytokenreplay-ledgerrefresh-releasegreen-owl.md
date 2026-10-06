# DeriveBSD rev0540 session review — authority-token replay proof

Generated for: `2026-06-13r571`

## Priority risk addressed

The real FreeBSD host-smoke lane had replayable host probes, command-shape digests, and strict proof-bundle validation, but media-command authority still had a softer seam: `mdconfig` and `fstyp` rows could carry digest-shaped stdout evidence without enough local replay material to prove the md unit and filesystem token were the exact authority consumed by later commands.

Rev0540 closes that gap. The receipt now records replayable authority-token fields for `mdconfig` attach and `fstyp` verification. The validator recomputes the stdout digests, checks the stripped token, and requires the same md unit to flow through `fstyp`, read-only `mount`, and `mdconfig -d` before worker launch.

## Concrete changes

- `tools/freebsd/run_removable_media_local_fallback_host_smoke.py` records `observed_value`, `observed_stdout_text`, and `observed_value_key` for mdconfig/fstyp authority rows.
- `tools/freebsd/validate_removable_media_local_fallback_host_smoke_receipt.py` replays mdconfig/fstyp stdout digests and rejects authority-token drift.
- The validator now binds the mdconfig-emitted md unit across `fstyp`, read-only mount, and detach command shapes.
- `tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py` adds tamper regressions for mdconfig stdout replay drift and detach-target drift.
- `spec/removable.media.local.freebsd.host.smoke.receipt.schema.json`, validation simulations, proof-bundle example, generated cube artifacts, and front doors were refreshed for `2026-06-13r571`.

## Audit/refactor note

The audit/refactor stayed on the implementation seam rather than adding registry mass. The host-smoke command row shape now uses the same replayable token pattern for host probes, mdconfig authority, and fstyp authority, reducing future receipt-import ambiguity.

## Open risks

- A real non-simulated FreeBSD host proof bundle is still absent.
- `docs/00-index.md` remains exactly at the line budget and close to the byte budget; the compact front door should be used first.
- The canonical JSON profile remains restricted no-float JCS/I-JSON, not full arbitrary-number RFC 8785 JCS.

# DeriveBSD rev0539 session review — host-probe replay proof

Generated for: `2026-06-13r570`

## Priority risk addressed

The FreeBSD host proof path had already started validating command-shape digests and exact proof-tool sets, but the host-probe rows were still mostly digest-shaped. A future receipt could carry a `stdout_sha256` and top-level `host.host_probe_*` values without giving the importer enough local material to replay the probe token binding.

Rev0539 makes that seam more concrete: host probe rows now carry the parsed value, the raw probe stdout text, and the host-field key that value is supposed to populate. The validator recomputes the stdout digest, rejects multi-token stdout, and checks that the stripped probe token equals the matching `host.*` value.

## Concrete changes

- `tools/freebsd/run_removable_media_local_fallback_host_smoke.py` records `observed_value`, `observed_stdout_text`, and `observed_value_key` for each host probe before compile, makefs, mdconfig, or mount authority.
- `tools/freebsd/validate_removable_media_local_fallback_host_smoke_receipt.py` replays host-probe stdout digests and rejects probe value drift before proof acceptance.
- `spec/removable.media.local.freebsd.host.smoke.receipt.schema.json` adds the `hostProbeResult` surface so replayable probe evidence is schema-visible.
- `tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py` adds tamper regressions for probe value drift and stdout replay drift.
- Generated schema/audit/checkset/context artifacts and front doors were refreshed for `2026-06-13r570` without increasing the front-door budget.

## Audit/refactor note

This cut avoided a new registry family. The audit/refactor was concentrated on the riskiest live seam: whether a future imported FreeBSD receipt can be checked from its own evidence rather than trusted as a loose JSON assertion.

## Open risks

- A real non-simulated FreeBSD host proof bundle is still absent.
- The compact front door helps, but `docs/00-index.md` remains close to the budget ceiling.
- The canonical JSON profile remains restricted no-float JCS/I-JSON, not full arbitrary-number RFC 8785 JCS.

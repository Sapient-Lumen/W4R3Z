# DeriveBSD-rev0536-2026.06.12.22.32-hostproofbundle-strictjson-releasegreen-swan

## Outcome

rev0536 reduces two concrete risks without adding a broad registry layer: future real FreeBSD host proof now has a strict import/finalization path, and checked-in JSON now has release-critical duplicate-key rejection.

## Material changes

- Added `tools/freebsd/finalize_removable_media_local_fallback_host_proof_bundle.py`, `spec/removable.media.local.freebsd.host.proof.bundle.schema.json`, `spec/examples/removable.media.local.freebsd.host.proof.bundle.json`, and `tools/check_removable_media_local_fallback_freebsd_host_proof_bundle.py`.
- Extended `tools/freebsd/collect_removable_media_local_fallback_host_proof.sh` so a real FreeBSD operator run validates the receipt, writes the proof bundle, and prints both `receipt_sha256` and `bundle_sha256`.
- Added `tools/check_json_duplicate_key_rejection.py` and refactored schema/example/kind readers to use duplicate-key rejecting JSON loads.
- Added `docs/current/start-here-now.md` as the small operating front door while keeping `docs/00-index.md` inside the existing line budget.
- Refreshed generated docs, schema audit, schema refactor backlog, hygiene checkset manifest, and the canonical release ledger example for `2026-06-12r567`.

## Validation

- Release-critical hygiene: 38/38 passed, result `passed`.
- Schema-cube-audit hygiene: 3/3 passed, result `passed`.
- Schema audit counts: 457 schemas, 469 examples.
- Hygiene checkset counts: 371 top-level check scripts, 38 release-critical checks.

## Still open

- Real non-simulated FreeBSD host proof still needs to be collected on a FreeBSD machine.
- `docs/00-index.md` is still at the front-door line ceiling; use `docs/current/start-here-now.md` first.
- Seven lower-priority schema refactor backlog items remain open.

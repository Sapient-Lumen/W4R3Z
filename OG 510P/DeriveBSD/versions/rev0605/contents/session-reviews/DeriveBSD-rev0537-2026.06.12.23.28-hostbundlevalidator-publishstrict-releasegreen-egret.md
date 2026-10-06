# DeriveBSD-rev0537-2026.06.12.23.28-hostbundlevalidator-publishstrict-releasegreen-egret

## Outcome

rev0537 turns the FreeBSD host-proof import path from a finalized JSON blob into a revalidated proof bundle: the bundle validator rechecks the original receipt bytes, canonical receipt digest, host-smoke validator result, and current tool digests. The pass also refactors the publish-session checker family onto the shared strict JSON loader so duplicate-key behavior is not left to local parser drift.

## Material changes

- Added `tools/freebsd/validate_removable_media_local_fallback_host_proof_bundle.py` and wired it into `tools/freebsd/collect_removable_media_local_fallback_host_proof.sh`.
- Updated the host-proof bundle finalizer, schema, and example for `2026-06-12r568`, including the bundle validator in the tool-digest binding set.
- Extended `tools/check_removable_media_local_fallback_freebsd_host_proof_bundle.py` so default mode rejects checker-only simulations and tampered receipt digests, while explicit checker-simulation mode remains available for non-proof examples.
- Refactored the `tools/check_publish_session_contract.py` family onto `tools/cube_digest_lib.py` strict JSON loading, removing local `json.loads`/`import json` drift from the publish-session checker cluster.
- Refreshed generated docs, schema audit, schema refactor backlog, hygiene checkset manifest, and the canonical release ledger example for `2026-06-12r568`.

## Validation

- Release-critical hygiene: 38/38 passed, result `passed`.
- Schema-cube-audit hygiene: 3/3 passed, result `passed`.
- Schema audit counts: 457 schemas, 469 examples.
- Hygiene checkset counts: 371 top-level check scripts, 38 release-critical checks.

## Still open

- Real non-simulated FreeBSD host proof still needs to be collected on a FreeBSD machine.
- `docs/00-index.md` is still at the front-door line ceiling and has byte-growth warnings; use `docs/current/start-here-now.md` first.
- Seven lower-priority schema refactor backlog items remain open.
- The canonical JSON profile remains intentionally restricted/no-float rather than full arbitrary-number RFC 8785 JCS.

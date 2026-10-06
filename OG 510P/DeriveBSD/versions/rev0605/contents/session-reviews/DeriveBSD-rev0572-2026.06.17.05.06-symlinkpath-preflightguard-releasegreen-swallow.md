# DeriveBSD-rev0572-2026.06.17.05.06-symlinkpath-preflightguard-releasegreen-swallow

## Focus

This revision stays on the riskiest incomplete lane: the first real FreeBSD host-proof run. It avoids adding a new evidence family and instead closes a path-handling seam that could route scarce handoff bytes or import roots through operator-supplied symlinks before the guarded Python verifier/importer refused them.

## Substantive changes

- `tools/freebsd/collect_removable_media_local_fallback_host_proof.sh` now refuses a symlinked `DERIVEBSD_HOST_PROOF_HANDOFF_DIR` before FreeBSD/root preflight, overwrite checks, or any `receipt.json`, `bundle.json`, or `SHA256SUMS` writes.
- `tools/freebsd/collect_import_removable_media_local_fallback_host_proof.sh` now refuses symlinked handoff and import-root paths before host-proof collection or import, and no longer pre-creates `IMPORT_ROOT` with shell `mkdir -p`.
- Safe import-root creation remains inside `tools/freebsd/import_removable_media_local_fallback_host_proof_handoff.py`, where the existing import-root guards and atomic publish behavior are already exercised.
- Release-critical handoff and collect/import checks now include preflight-order regressions proving the symlink refusals happen before FreeBSD/root preflight, before Python verifier fallback, and without mutating an import-root symlink target.
- The real-host operator packet and current host-smoke docs now make non-symlink handoff/import-root paths an explicit operator requirement, and current/generated surfaces were refreshed to `2026-06-17r600`.

## Audit/refactor note

The refactor here is deliberately small: path trust moved out of implicit shell behavior and into explicit shell preflight refusals, while import-root creation was removed from the one-shot shell wrapper and left to the guarded Python importer. This reduces duplicated path authority and makes the first real-host run less dependent on later audit catching a bad path.

## Validation

- release-critical profile: 49/49 passed; result `passed`; run_complete `true`.
- schema-cube-audit profile: 3/3 passed; result `passed`.
- spec examples: 469 validated.
- strict JSON duplicate-key scan: 1452 JSON files scanned.
- schema count: 457 schemas, 469 examples.
- hygiene checkset: 382 hygiene-referenced checks, 291 deep-contract checks, 49 release-critical checks.

## Remaining caveat

This still does not include non-simulated FreeBSD host proof. The next true milestone remains a real `15.1-RELEASE` host run, returned handoff, strict import, and audit as `real-host-proof`.

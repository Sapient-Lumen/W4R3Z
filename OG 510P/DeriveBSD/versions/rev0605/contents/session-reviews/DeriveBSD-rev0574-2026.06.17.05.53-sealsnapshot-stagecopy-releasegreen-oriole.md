# DeriveBSD-rev0574-2026.06.17.05.53-sealsnapshot-stagecopy-releasegreen-oriole

## Focus

Rev0574 keeps the session on the riskiest unfinished lane: the first non-simulated FreeBSD host-proof handoff and the transport/import path that must preserve it. The concrete risk addressed here is smaller than a new feature but important for first use: the deterministic sealer verified a handoff and then read from the mutable source directory while writing the archive. That left a post-verification reread seam in the preferred sealed transport path.

## Substantive changes

- Added `HANDOFF_SEAL_SNAPSHOT_POLICY` to `tools/freebsd/host_proof_contract.py`.
- Changed `tools/freebsd/seal_removable_media_local_fallback_host_proof_handoff.py` so it verifies the source handoff, copies allowed members through the importer's finite nofollow staging copy path, revalidates the staged snapshot, and writes the deterministic ZIP from staged bytes.
- Surfaced the seal snapshot policy in sealer output so transport evidence names the copied-snapshot boundary.
- Extended `tools/check_removable_media_local_fallback_freebsd_host_proof_handoff_seal.py` with a staged-copy regression proving archive contents follow the copied handoff snapshot rather than a mutable source reread after verification.
- Refreshed proof-bundle examples, current proof docs, generated docs, schema/checkset examples, README, CHANGELOG, and hygiene ledgers to `2026-06-17r602`.

## Audit/refactor notes

The audit found a useful seam where earlier work had made import/unseal robust but left sealing less disciplined. Rather than introduce a new proof status or another registry, the sealer now reuses the existing importer copy primitive that already enforces finite allowed members, nofollow source opens, and copy-time mutation checks. That is a substance-first refactor: the transport helper now shares the same byte-acquisition semantics as import instead of carrying a softer one-off read path.

The front-door index exceeded its byte ratchet after documenting the new cut. The fix was to compress existing index prose and keep the budget, not raise the limit.

## Validation

- Release-critical profile: 49/49 passed; failed=0; timed_out=0.
- Schema-cube-audit profile: 3/3 passed; failed=0; timed_out=0.
- Spec examples validated: 469.
- Schemas total: 457.
- Hygiene-referenced check scripts: 382.
- Deep-contract checks: 291.
- Strict JSON duplicate-key scan: 1455 JSON files scanned.
- Empty `validation/freebsd-host-proof-imports/` root preserved for future checked-in real-host proof imports.

## Caveat

This revision still does not contain a non-simulated FreeBSD host receipt. The true milestone remains a real `15.1-RELEASE` host run, returned handoff, strict import, and audit as `real-host-proof` with `primary-production` target-tier evidence.

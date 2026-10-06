# DeriveBSD rev0605 session review — snapshot admission / repository guard / marten

## Cut

- Package revision: `DeriveBSD-rev0605-2026.06.18.10.40-snapshotadmission-repositoryguard-marten.zip`
- Semantic cube cut: `2026-06-18r630`
- Session posture: runtime-first; no new doctrine-only schema family; no new release-critical checker added solely to raise bureaucracy.

## Highest-risk seam addressed

rev0604 made checked-in package payload bytes the source of truth, but the runtime still accepted a projected catalog as the only repository-shaped index. That was the next completion-risk gap before any real FreeBSD package/base resolver: a future resolver must admit a repository snapshot before package selection, so the fixture resolver now exercises that ordering.

## Substantive runtime changes

- Added admitted offline fixture repository snapshot support at `validation/runtime-package-repository/current/snapshot.json`.
- Added `tools/gen_runtime_fixture_repository.py` to generate the repository snapshot and catalog projection from checked-in fixture package payload bytes.
- Updated `tools/derive_runtime.py` so `lock` admits the snapshot before catalog projection and rejects:
  - stale snapshot bytes relative to the catalog's snapshot reference;
  - catalog/snapshot platform or package-set drift;
  - catalog/snapshot material-row drift;
  - snapshot/payload identity, version, platform, origin, runtime-use, digest, or dependency drift;
  - catalog/payload drift;
  - missing dependency targets;
  - dependency cycles;
  - package material digest/size mismatch;
  - mutable `:latest` microVM closure names.
- Carried repository snapshot policy/digest/row-digest evidence through lock, plan, artifact, package material manifest, activation surface, and explain output.
- Kept the runtime truth claim explicit: this is still finite offline fixture repository admission, not authoritative FreeBSD package-index resolution.

## Audit/refactor work

- Replaced hand-maintained fixture-repository/catalog drift with a generator whose source of truth is the package payload material already consumed by the runtime.
- Hardened `package_catalog_digest()` so runtime-attached `_repository_snapshot` cache data cannot alter on-disk catalog projection identity.
- Regenerated only affected current evidence surfaces: runtime golden thread, host-smoke/proof examples, real-host work order, generated docs, schema-audit/checkset/backlog examples, and release-critical ledger.
- Trimmed the front-door index instead of raising its byte budget.

## Evidence

- `tools/check_runtime_golden_thread.py`: passed.
- `tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`: passed.
- `tools/check_removable_media_local_fallback_freebsd_host_proof_bundle.py`: passed.
- `tools/check_removable_media_local_fallback_freebsd_host_proof_work_order.py`: passed.
- `tools/check_current_generated_surface_sync.py`: passed.
- Release-critical hygiene ledger: 52 checks completed, 52 passed, 0 failed, 0 timed out.
- Python bytecode artifacts: clean.
- Validation logs: clean.

## Honest boundary

rev0605 still does not resolve signed or freshness-protected real FreeBSD repository metadata, consume actual pkg/base archives, construct a ZFS boot environment, run `bectl`, launch bhyve, mutate a host, or import real FreeBSD proof. It closes the fixture-side ordering seam so the next real resolver has a stricter executable shape to replace.

## Recommended next cut

The next high-substance move is to introduce a real-repository metadata adapter shape that can ingest a captured FreeBSD pkg repository snapshot in offline mode and project the same admitted-snapshot evidence fields, while still refusing network use and mutable references in the cloudtainer. Do not add more proof envelopes until at least one real repository snapshot can be captured, hashed, admitted, and compared against fixture semantics.

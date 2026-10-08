# rev0654 — C++ sync manifest diff/planning seam

## Mission fit

AnonSync is a C++ peer-to-peer file synchronization system. After rev0653, the cube could turn a local directory into a validated folder manifest, but it still could not answer the core sync question: given my manifest and a peer manifest for the same folder, what should happen next?

Rev0654 adds the first deterministic planner for that question. It does not transfer bytes or mutate disk. It produces an auditable plan that later peer/session, transfer, mutation-ledger, and conflict-resolution layers can execute idempotently.

## C++ additions

Public API additions in `cpp/anonsync_core/include/anonsync_core.hpp`:

- `enum class SyncPlanAction`
  - `Noop`
  - `FetchRemoteFile`
  - `PublishLocalFile`
  - `ApplyRemoteTombstone`
  - `PublishLocalTombstone`
  - `RecordConflict`
- `enum class SyncLineageRelation`
  - `Equal`
  - `LocalNewer`
  - `RemoteNewer`
  - `Concurrent`
- `struct SyncManifestPlanEntry`
- `struct SyncManifestDiffPlan`
- `std::string sync_manifest_entry_version_digest(const SyncManifestEntry& entry)`
- `SyncValidationResult build_sync_manifest_diff_plan(const SyncFolderManifest& local, const SyncFolderManifest& remote, SyncManifestDiffPlan& out)`

## Audit/refactor finding

A peer-to-peer sync comparison cannot treat publisher-bound entry digests as file-version identity. A `SyncManifestEntry` intentionally carries a `device_id` for the device publishing that folder manifest. If device A and device B both know the same file version, their publisher-bound entry digests can differ solely because they were published by different devices.

Rev0654 adds `sync_manifest_entry_version_digest` for the comparison layer. This digest excludes the publisher `device_id` while still binding folder id, path, kind, size, content hash, chunk digest, lineage digest, and conflict-set id. `sync_manifest_entry_digest` remains useful as publisher-bound evidence inside `SyncFolderManifest` identity. `build_sync_manifest_diff_plan` carries both forms so reviewers can see why a plan no-ops a cross-device match without losing the publisher evidence.

## Planner behavior

`build_sync_manifest_diff_plan`:

1. validates both folder manifests;
2. rejects different folder ids;
3. rejects same-device peer comparisons;
4. binds local and remote manifest digests into the plan;
5. walks both sorted manifest entry lists by canonical path;
6. classifies missing local entries as remote fetch or remote tombstone application;
7. classifies missing remote entries as local file or local tombstone publication;
8. compares shared paths by publisher-neutral version digest and lineage relation;
9. records conflicts for concurrent lineage or equal-lineage divergent content;
10. emits needed remote chunks only when no local chunk has the same SHA-256 and length.

## Validation evidence

- Release configure/build passed.
- Release CTest passed: `100% tests passed, 0 tests failed out of 27`.
- `--selftest-sync-domain-model` passed: `anonsync_core sync domain model selftest passed=54 failed=0`.
- ASAN/UBSAN sync-domain selftest passed with the same summary.
- Package validator passed.

## Still not claimed

Rev0654 does not persist manifest state, exchange manifests over a peer protocol, transfer chunks, stage partial files, apply file writes, apply tombstones to disk, materialize conflict copies, watch OS filesystem events, discover peers, perform NAT traversal, or run as a sync daemon. It only makes the next decision boundary explicit and testable in C++.

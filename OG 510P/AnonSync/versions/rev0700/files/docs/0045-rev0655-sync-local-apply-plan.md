# rev0655 — C++ sync local apply-plan seam

## Mission fit

AnonSync is a C++ peer-to-peer file synchronization product. Rev0655 keeps the cube pointed at that product by moving from "what differs between two peer manifests?" to "what local filesystem intent should be prepared before any bytes are written?"

Rev0654 could compare two validated folder manifests and decide whether an entry should be fetched, published, deleted, ignored, or recorded as a conflict. That was necessary but still too abstract for a safe sync engine: a production-style sync daemon must know where inbound file bytes are staged, where the final target lives, how tombstones map to local deletion, and how conflicts preserve the local version while materializing the peer version.

## C++ changes

Rev0655 adds these public C++ types and function to `cpp/anonsync_core/include/anonsync_core.hpp`:

- `SyncLocalApplyAction`
- `SyncLocalApplyOptions`
- `SyncLocalApplyPlanEntry`
- `SyncLocalApplyPlan`
- `build_sync_local_apply_plan`

The implementation lives in `cpp/anonsync_core/src/sync_domain.cpp`. It takes a validated `SyncManifestDiffPlan` plus explicit local and staging roots and emits deterministic local intents:

- `FetchRemoteFile` → `StageRemoteFile` under an out-of-tree staging root.
- `ApplyRemoteTombstone` → `DeleteLocalPath` under the synchronized folder root.
- `RecordConflict` → `PreserveConflictCopy`; for remote files it also stages the peer version.
- `PublishLocalFile` → `AdvertiseLocalFile`.
- `PublishLocalTombstone` → `AdvertiseLocalTombstone`.
- `Noop` → `Noop`.

Each local apply entry carries the canonical sync path, source diff action, local action, absolute target path, optional absolute staging path, optional absolute conflict-copy path, digest evidence, version digest evidence, conflict set id, reason, needed remote chunks, and a deterministic `sync-local-apply:v1:` idempotency key.

## Audit/refactor finding

The audit finding for this turn is that `SyncManifestDiffPlan` was still a reconciliation decision, not a safe local mutation boundary. Rev0655 refactors the sync-domain layer so disk-facing code can consume a checked intent object before any future file write/delete/rename implementation exists.

The refactor also adds self-validation of constructed manifest diff plans and constructed local apply plans before returning success. This keeps generated plan shape under the same fail-closed discipline as manifest entries and folder manifests.

## Safety properties added

- The local root must exist, must be a directory, and must not be a symlink.
- The staging root must be separate from the synchronized folder tree; staging under the sync root is rejected so `.part` files are not re-indexed as user content.
- Target, staging, and conflict-copy paths are resolved through the portable `NormalizedSyncPath` policy and must stay under their configured roots.
- Conflict planning retains needed remote chunks when the remote conflict side is a file.
- Local apply idempotency keys bind folder id, local/remote device ids, manifest digests, path, source action, local action, entry digests, version digests, and conflict set id.

## Validation

Release validation was rerun after the local apply-plan/refactor changes:

```text
100% tests passed, 0 tests failed out of 27
```

The sync-domain selftest now covers the local apply seam:

```text
anonsync_core sync domain model selftest passed=62 failed=0
```

A narrow AddressSanitizer/UndefinedBehaviorSanitizer build of `sync_domain.cpp` plus the sync-domain harness also passed with the same selftest summary. Full CMake sanitizer coverage remains heavy because older non-sync translation units are large; rev0655 records the narrow sanitizer scope explicitly.

The package validator is `tools/validate_rev0655_sync_local_apply_plan.py`.

## What this still does not prove

Rev0655 does not write chunk bytes, fsync staged content, atomically rename files into place, delete target files, materialize conflict copies, persist manifest/index state, exchange manifests with peers, authenticate a peer session, perform LAN/WAN discovery, handle NAT traversal, or run as a daemon.

The next code-bearing seam should consume `StageRemoteFile` intents with partial-file staging, chunk-write accounting, full-file SHA-256 verification, fsync, crash cleanup, and atomic rename before claiming a remote file is applied.

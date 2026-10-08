# Revision notes — rev0968

## Product move

Rev0968 makes multi-page causal-version browsing fail closed against source
change. `anonsync_sync versions` accepts:

```text
--source-cutpoint v1:OPERATION_SET_SHA256:PAYLOAD_SNAPSHOT_SHA256
```

The first page returns that canonical token. Every later page can bind itself
to the same exact active operation set and retained payload-store snapshot.
Operation or payload drift completes as a typed owner-visible failure instead of
silently mixing page sources.

## C++ implementation

- Added `SyncReplicaHistoricalVersionSourceCutpoint`, strict canonical
  encode/decode/validation, and an optional expected cutpoint in the shared
  historical-version query.
- Added typed source-change stages for operation-set drift before payload work,
  operation-set drift during payload observation, and payload-snapshot drift.
- Reordered inspection so expected operation-set and cursor failures occur
  before the complete payload-store scan.
- Bracketed that payload scan with exact replica operation-set snapshots.
- Returned the exact operation-set digest and canonical source token with every
  inventory.
- Added service failure class and source-change-stage state without introducing
  another action lane or terminating the daemon.
- Corrected a dead diagnostic path by serializing the already-populated class
  and stage on the exact transient `last_step` as well as stable retained
  historical status; later network steps may legitimately replace `last_step`.
- Advanced peer status to `anonsync.peer-service.status.v13` and the local
  versions response to `anonsync.local-historical-versions.response.v3`.
- Extended the owner socket with an optional fourth source-token field while
  preserving the rev0967 three-field and legacy default forms.
- Added `--source-cutpoint` to the shipping CLI.
- Extended the real two-peer service regression through an unrelated causal
  mutation, exact early source-change classification, same-PID survival, stale
  result clearing, and failure-counter settlement.

## Adjacent audit/refactor

Rev0967 described page cutpoints but left comparison to callers after the fact.
Its cursor only bound one selected historical operation, so unrelated causal
insertions or retained-payload changes could produce a mixed listing. Rev0968
moves that consistency check into the owner request and reports exact typed
failure stages.

The audit also rejected `state_generation` as the source token. That value
includes unrelated liveness writes and would create false failures. The
operation-set digest is the exact causal projection input; visible and state
values remain diagnostics.

## Compatibility

- Existing `versions\n` requests remain the global default query.
- Rev0967's three-field `versions-query LIMIT PATH_HEX CURSOR` frame remains
  accepted.
- New clients send a fourth source field or `-` and require the v3 response.
- This is a local owner-control schema change, not a reconciliation wire-protocol
  generation change.

## Validation

Exact rev0968 source passed the complete GCC 14.2 Debug graph (527/527 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 393 folder-owner, 7 folder-process, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 115 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 237/237 checks. A clean-root Clang 17 Debug product dependency graph completed 238/238 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error, including the focused 393-check folder-owner suite in 28.51 seconds at 1,342,052 KiB peak RSS and the 115-check local-control suite. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic.

## Nonclaims

Rev0968 does not add durable version pins, retention windows, quotas, garbage
collection, chronology, conflict browsing, batch restore, directory restore, or
cross-owner snapshot transactions. It strengthens bounded browse consistency;
restore still re-proves all mutable authority.

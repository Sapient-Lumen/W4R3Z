# Revision notes — rev0966

Rev0966 exposes retained causal file predecessors through the owner-only linked-peer service and restores one exact predecessor by publishing its bytes through
the existing rooted atomic publisher and ordinary local causal scanner.

## Mission move

AnonSync already retained immutable superseded file operations and append-only
content payloads, but an owner could not discover or recover them through the
shipping service. This revision adds the first bounded operable version-recovery
slice without importing the discarded prototype, adding a second byte store, or
forking the synchronization algorithm.

## C++ implementation

- Added `anonsync_sync versions --socket ABSOLUTE_SOCKET` and
  `anonsync_sync restore --socket ABSOLUTE_SOCKET --operation LOWERCASE_SHA256`.
- Added strict `versions\n` and `restore OPERATION_ID\n` local protocols with
  PID-bound responses and the existing exact mode-0600/parent-permission checks.
- Added one history-action lane to the mutex-linearized action snapshot. Exact
  repeated requests coalesce by generation; a different pending history action
  is rejected; drain closes admission without losing accepted generations.
- Added a default 64-entry and hard 1,024-entry causal-version projection.
- Inspection performs one complete payload-store snapshot and one replica
  snapshot, counts every active non-visible file operation, and reports exact
  payload presence and immediate restore readiness.
- Restore re-proves the selected active operation, sole visible head, catalog,
  rooted current path, targeted payload descriptor, and guarded visible-state
  digest before atomic replace/create.
- The selected bytes are committed through the ordinary prepared local-file
  scanner. The result must be a new operation that causally supersedes the
  current head; historical evidence is never reactivated or rewritten.
- Added service scheduling, explicit operator failures, counters, live/terminal
  rendering, and `anonsync.peer-service.status.v11`.

## Adjacent audit/refactor

The first bounded inventory implementation still cloned the entire active
operation set and complete visible-path projection. `SyncReplicaModel` now
provides a borrowed immutable active-operation visitor. Inspection performs one
per-candidate visible-path lookup and retains only a bounded max-heap of the
requested best entries before `std::sort_heap` emits canonical order. The
additional response storage is O(requested entries), not O(active operations).

The audit also corrected a stale overwrite-count oracle after the real-process
fixture gained an ordinary history edit, and restored the sealed rev0963 status-
v10 documentation expectation after an overly broad schema replacement.

## Mechanical validation

- Folder-owner regression: exact v1→v2 predecessor discovery, rooted v1 restore,
  new causal successor, immutable predecessor retention, deterministic bounded
  follow-up inventory, invalid/current/same-byte rejection, and exact recovery
  of a deleted file from behind its causal tombstone.
- Local-control regression: exact schemas, PID binding, coalescing, changed-
  request rejection, generation completion, post-drain rejection, mode-0600
  enforcement, and malformed operation-ID rejection.
- Real configured-service regression: two authenticated peers converge v2,
  owner inspection returns the exact retained v1 operation, owner restore
  creates a distinct successor, and both peers converge exact v1 bytes with
  two requests, two attempts, two completions, one inspection, one restore, and
  zero failures.

## Validation

Exact rev0966 source passed the complete GCC 14.2 Debug graph (527/527 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 92 network-model plus 41 generated-operation, 296 SQLite-owner, 379 folder-owner, 7 folder-process, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 107 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 219/219 checks. A fresh Clang 17 Debug product dependency graph completed 238/238 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error, including the 379-check folder-owner suite in 18.10 seconds at 1,338,192 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic.

## Nonclaims

The inventory is causal, not chronological. It covers only active superseded
file operations and only marks a candidate restorable while its exact immutable
payload remains present. Rev0966 does not add retention windows, pins, quotas,
Archive UX, garbage collection, conflict resolution, batch/directory restore,
rename identity, friendly timestamps, a GUI, or cross-owner filesystem/SQLite
atomicity.

See `EXPLICIT_CAUSAL_VERSION_INSPECTION_AND_ROOTED_RESTORE_AUDIT_rev0966.md`.

# Revision notes — rev0969

## Product move

Rev0969 prevents the shipping historical restore command from silently
replacing a path head that changed after the operator inspected it.

```text
anonsync_sync restore --socket ABSOLUTE_SOCKET \
    --operation HISTORICAL_OPERATION_SHA256 \
    --expected-current CURRENT_PRIMARY_OPERATION_SHA256
```

The current ID is copied from the selected version entry's
`current_primary_operation_id`. Restore fails closed unless that operation is
still the path's sole visible head.

## C++ implementation

- Added `SyncReplicaHistoricalVersionRestoreRequest` as the shared restore
  identity across CLI, socket, peer service, status, and folder owner.
- Added the typed source-change stage `restore_current_operation`.
- Performed the path-local exact-current check from the immutable replica model
  before catalog, rooted-path, or payload-store work.
- Preserved the later visible-state projection guard and all existing catalog,
  rooted publication, targeted payload, and ordinary successor-mint cutpoints.
- Added the strict owner frame
  `restore-exact HISTORICAL EXPECTED_CURRENT\n` and response schema
  `anonsync.local-historical-version-restore.response.v2`.
- Kept the rev0966 `restore HISTORICAL\n` frame and string owner overload as
  explicitly unbound compatibility paths; the shipping CLI requires the exact
  current head.
- Advanced live and terminal reporting to
  `anonsync.peer-service.status.v14`.
- Added stable and transient serialization of the full restore request.
- Added folder-owner, local-socket, and real configured-service stale-intent
  regressions.

## Adjacent audit/refactor

A content digest or timestamp was rejected as the restore precondition because
causally distinct operations may carry equal bytes. A complete rev0968 page
source token was also rejected because unrelated paths and retained payloads
would create false conflicts and force broader observation than the selected
restore needs.

The exact sole current operation is the minimum path-local validator. This is
analogous to a strong conditional update such as HTTP `If-Match`, while the
existing replica projection guard remains the later publication fence.

Restore request fields had also been duplicated across socket and service state.
The new shared request object makes full intent equality the coalescing and
status identity. A divergent unsealed rev0969 worktree/build was deleted before
validation and contributes no release evidence.

The complete process registry also caught a false filesystem oracle: test code
could enumerate an exact `.anonsync-publish-v1-...tmp` pathname and then read
it after normal atomic publication removed it. Both tree comparators now use
the product's exact lowercase-hex temporary-name grammar and skip only those
internal names before stat or read. The sync-once comparator now hashes in
bounded 1 MiB blocks rather than loading each file wholly into memory.

## Compatibility

- `versions` request and response schemas are unchanged.
- Reconciliation protocol generation remains unchanged.
- New shipping restores require `--expected-current` and use local response v2.
- The legacy owner-only local restore frame remains accepted and returns v1.
- Status clients must understand `anonsync.peer-service.status.v14` and the new
  `expected_current_operation_id` and
  `historical_version_restore_request` fields.

## Validation

Exact rev0969 source passed the complete GCC 14.2 Debug graph (527/527 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 397 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 119 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 247/247 checks. A clean-root Clang 17 Debug product dependency graph completed 238/238 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 397-check folder-owner suite in 22.24 seconds at 1,348,040 KiB peak RSS and the 119-check local-control suite. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0968 parent SHA-256 matched 3edbc700faa3f736321ae8f41aade11e2198985f3a1a0552b1a237e72d9d916f and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 568 files / 25,986,608 bytes with SHA-256 0d8b28b316b616dcd091fe374eff3468b36dfacc52749a39f7e14cb0c9851174.

## Nonclaims

Rev0969 does not add retention policy, durable pins, chronology, conflict
selection, batch or directory restore, quotas, collection, or a browse/restore
transaction. It makes the ordinary product command conditional on the exact
current causal head the operator reviewed.

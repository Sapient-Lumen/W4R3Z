# Exact-current-bound historical restore audit — rev0969

## Product defect

Rev0966 made retained causal predecessors restorable and rev0968 made a paged
history listing internally source-consistent. The shipping restore command,
however, still carried only the selected historical operation ID. Between the
operator reading a page and requesting restore, the same path could acquire a
new visible successor. The old command would then restore over that newer head
as long as the historical operation remained active and the later mutable-owner
reproofs succeeded.

That behavior is causally valid but operationally unsafe. It is the classic
lost-update shape: the operator reviewed one current head, but the state-changing
request was not conditional on that head still being current.

## Exact-current contract

The rev0969 shipping command is:

```text
anonsync_sync restore --socket ABSOLUTE_SOCKET \
    --operation HISTORICAL_OPERATION_SHA256 \
    --expected-current CURRENT_PRIMARY_OPERATION_SHA256
```

`--expected-current` is copied from the selected inventory entry's
`current_primary_operation_id`. The two IDs must be distinct canonical lowercase
SHA-256 operation IDs. The folder owner accepts the restore only when the target
path still has exactly one visible operation and that operation is the expected
current ID.

The precondition is intentionally path-local. Requiring rev0968's complete
history-page source token would reject harmless changes elsewhere and would bind
a state-changing request to an O(payload namespace) observation that restore
already re-proves independently. The exact sole current operation is the
smallest causal fact that prevents an unnoticed overwrite at the selected path.

## Why operation identity, not file bytes

A content digest is insufficient. Two distinct causal operations can carry the
same bytes while having different predecessors, conflict relationships, or
future synchronization consequences. The compare-and-restore condition binds
operation identity, not merely content equality or a timestamp. A conflict is
also not reduced to whichever deterministic primary happens to sort first: more
than one visible head fails the precondition.

This follows the same general lost-update discipline as HTTP `If-Match`: a
state-changing request is applied only when the previously observed current
validator still matches. RFC 9110 describes conditional requests as a way to
prevent one client from overwriting work performed in parallel and requires a
strong comparison for `If-Match`.

Reference: https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.1

Syncthing's Block Exchange Protocol similarly treats file name plus version as
the identity of transfer progress and requires progress for a changed version
to replace prior-version progress. That is not an AnonSync wire-compatibility
claim; it is evidence that content-location state and causal/version identity
must not be conflated.

Reference: https://docs.syncthing.net/specs/bep-v1.html

## Authority order

The exact-current check is performed from the immutable replica snapshot before
catalog observation, rooted destination inspection, or payload-store targeted
access. A stale request therefore does not pay or acquire those later mutable
authorities.

The existing restore path remains the publication authority:

1. validate the shared restore request;
2. snapshot and restore the causal replica model;
3. locate the active historical file operation;
4. require the exact sole current operation named by the request;
5. validate the canonical rooted path;
6. reject already-visible history, conflicts, or equal current bytes;
7. re-prove the catalog and current rooted file or absence;
8. open the exact retained historical payload through targeted access;
9. guard the complete visible-state digest and re-prove the historical/current
   operations and path view;
10. atomically replace or create the rooted file from the borrowed payload
    descriptor;
11. commit the guard and mint or adopt a new ordinary local causal successor.

The existing visible-state projection guard closes the later race. If any
causal writer changes the model after the early precondition but before
publication, the guard fails or its guarded model no longer matches. The new
stage is therefore an early no-work rejection, not a substitute for the later
cross-owner cutpoints.

## Typed failure and operator evidence

A stale exact-current request completes in the existing serialized historical
action lane as:

```text
failure_class: source_changed
source_change_stage: restore_current_operation
```

The daemon remains alive. Stable `historical_versions` status retains the exact
historical operation and expected current operation, while the matching
transient `last_step` carries the same shared request object. Live and terminal
status advance to `anonsync.peer-service.status.v14`.

The owner-only exact local frame is:

```text
restore-exact HISTORICAL_OPERATION EXPECTED_CURRENT_OPERATION\n
```

Its response is
`anonsync.local-historical-version-restore.response.v2` and echoes both IDs.
The rev0966 unbound `restore OPERATION\n` frame and string C++ overload remain
accepted only for local protocol compatibility. The shipping CLI never emits
that frame. Consequently, rev0969 closes stale-browse overwrite in the product
path but does not pretend an owner deliberately using the legacy raw frame has
received a compare-and-restore guarantee.

## Adjacent refactor

Before rev0969, restore identity was split across a string operation ID in the
socket, another string in the service, and a query object used only for
inspection. That made request coalescing and status evolution prone to forgetting
one field.

`SyncReplicaHistoricalVersionRestoreRequest` is now the one shared value object
through CLI validation, local frame parsing, mutex-linearized pending action,
peer-service generation identity, transient step evidence, stable status, and
folder-owner execution. Equality of the complete request controls coalescing;
a different expected current operation cannot replace or coalesce with pending
work.

A cloudtainer audit also found a second unsealed rev0969 tree and build using a
divergent restore design. They were removed before authoritative validation.
No result from that tree is release evidence.

The complete process registry then exposed a separate oracle race. Two Python
tree comparators enumerated the product's exact atomic-publication temporary
name and attempted to read it after the ordinary rename or unlink cutpoint.
That internal pathname is explicitly excluded by the C++ folder observer and
is not user data. Both process comparators now mirror the exact lowercase-hex
`sync_atomic_file_publication_temp_basename_is_exact` grammar before any stat
or read. The sync-once comparator was also changed from whole-file
`read_bytes()` to bounded 1 MiB streaming SHA-256, removing an avoidable
large-file memory spike. Broad dotfile suppression and generic missing-file
retries were rejected because they would hide real user-visible namespace
changes.

## Regression strategy

The focused folder-owner regression holds the exact payload store's exclusive
mutation lease while issuing a stale exact-current request. The required typed
`restore_current_operation` failure still occurs. Had the implementation reached
targeted payload access first, it would instead have reported lease contention.
The regression also proves replica, catalog, and rooted bytes remain unchanged.

The real configured-service regression:

- creates v1 and v2;
- inspects v1 and records v2 as the exact current head;
- restores v1 with that bound intent and observes convergence;
- replays the now-stale v1/v2 intent;
- observes a same-PID typed `restore_current_operation` failure;
- verifies stable request/failure evidence and settled counters; and
- continues through source-cutpoint pagination and later service recovery work.

The local-socket regression covers exact framing, v2 response echo, full-request
coalescing, different-current rejection, malformed and equal IDs, drain
serialization, mode enforcement, and retained v1 legacy framing.

## Nonclaims and next edge

Rev0969 does not create a durable user transaction spanning browse and restore.
It does not pin history, add retention windows, friendly chronology, conflict
selection, directory restore, batch restore, quotas, or garbage collection. A
legacy raw local frame remains intentionally unguarded. The exact-current
operation can also become stale after a failed request; the operator must inspect
again and deliberately choose against the new head.

The next useful version-lifecycle work should define explicit retained-version
reachability and policy before any collector is written. Restore safety now has
a path-local compare-and-restore primitive suitable for that future UI.

## Validation

Exact rev0969 source passed the complete GCC 14.2 Debug graph (527/527 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 397 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 119 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 247/247 checks. A clean-root Clang 17 Debug product dependency graph completed 238/238 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 397-check folder-owner suite in 22.24 seconds at 1,348,040 KiB peak RSS and the 119-check local-control suite. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0968 parent SHA-256 matched 3edbc700faa3f736321ae8f41aade11e2198985f3a1a0552b1a237e72d9d916f and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 568 files / 25,986,608 bytes with SHA-256 0d8b28b316b616dcd091fe374eff3468b36dfacc52749a39f7e14cb0c9851174.

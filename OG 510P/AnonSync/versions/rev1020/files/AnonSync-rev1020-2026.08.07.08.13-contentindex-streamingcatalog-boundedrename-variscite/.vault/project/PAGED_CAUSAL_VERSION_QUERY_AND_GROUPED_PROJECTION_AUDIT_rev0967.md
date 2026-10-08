# Paged causal-version query and grouped projection audit — rev0967

## Heart of the mission

AnonSync exists to replace Resilio Sync with one practical C++ folder-sync
application. Earlier-file recovery is useful only when an owner can discover
all eligible retained values through the running service without private-store
knowledge, unbounded waiting, or another synchronization engine.

Rev0966 made causal predecessors visible and restorable, but its bounded result
was not fully navigable. Once more than the requested limit existed, status
could truthfully say that results were truncated while offering no operation to
reach the omitted suffix. Rev0967 closes that product gap with path filtering
and deterministic continuation while preserving the same owner socket, service
scheduler, causal model, payload store, rooted restore path, and status surface.

## Audit finding: bounded output, quadratic work

The first inspection implementation retained only K response entries, but for
each active operation it called `visible_path(canonical_path)`. That lookup
rescanned all A active operations. With one operation at each of many paths,
one 64-entry request therefore performed O(A²) operation examinations.

A second quadratic edge lived inside one long path. The visible projection
asked whether every candidate was superseded by any other candidate, producing
O(P²) comparisons for P operations at that path. Long edit histories are
exactly the workload a version browser creates, so this was not theoretical
cleanup.

The correction is shared model infrastructure, not a history-specific shadow
index:

1. collect one vector of pointers to active immutable operations;
2. sort by canonical path and operation ID;
3. present each equal-path range as a borrowed span;
4. aggregate the maximum causal-context counter per actor once; and
5. mark a candidate visible exactly when that aggregate does not cover its dot.

The own-actor context invariant is `dot.counter - 1`, so an operation cannot
supersede itself through the aggregate. Another operation supersedes a candidate
exactly when its context covers that candidate's actor dot, which is equivalent
to the public pairwise predicate. The regression retains the pairwise algorithm
as an independent oracle over a 258-operation history with a concurrent remote
branch.

`visible_paths()` now uses the same visitor, so the refactor removes repeated
whole-model scans from ordinary complete visible projections as well as version
inspection.

## Owner query contract

The public query is:

```text
SyncReplicaHistoricalVersionQuery
    maximum_entries: 1..1024, default 64
    canonical_path: optional canonical relative path
    start_after_operation_id: optional lowercase SHA-256 operation ID
```

The CLI exposes it as:

```text
anonsync_sync versions --socket ABSOLUTE_SOCKET \
    [--path CANONICAL_RELATIVE_PATH] \
    [--after LOWERCASE_SHA256] [--limit 1..1024]
```

The internal mode-0600 Unix-socket frame is deliberately strict:

```text
versions-query LIMIT PATH_HEX_OR_DASH CURSOR_OR_DASH\n
```

A path is lowercase hex rather than whitespace-delimited text. This preserves
arbitrary permitted pathname bytes and leaves `-` available as an unambiguous
absence marker. Decimal limits are canonical and leading-zero forms are
rejected. Legacy `versions\n` remains accepted as the exact global default
query.

The server echoes the exact query in
`anonsync.local-historical-versions.response.v2`. The client validates the
schema, field count, returned path, limit, cursor, request generation, terminal
class, rejection reason, server PID, connected Unix peer PID, socket mode, and
parent permissions.

## Pagination semantics

Inventory ordering remains deterministic:

1. canonical path byte order;
2. actor device ID;
3. actor epoch;
4. causal counter descending; and
5. operation ID.

A cursor is the operation ID at the previous page tail. It is advisory browse
state, never restore authority. Before selecting a suffix, the folder owner
requires the cursor to name an active file operation that is still superseded
and, when a path filter is present, belongs to that exact path. A stale cursor
cannot silently become an omission boundary.

The result reports:

- the exact query;
- total historical file operations in query scope;
- historical operations strictly after the cursor;
- exact payload-presence and immediate-restore-ready totals for the whole
  selected scope;
- at most K canonical entries;
- `truncated`; and
- `next_start_after_operation_id`, equal to the returned tail only when a
  further entry exists.

Counts for payload presence and restore readiness describe the whole selected
scope rather than only the current page. `historical_file_operation_count_after_cursor`
is the value that determines page truncation.

Separate pages may observe separate replica or payload cutpoints. Every page
already carries the source replica generation, visible-state digest, payload
snapshot digest, and scan work. A future UI should discard accumulated pages
and restart when those cutpoints change. Rev0967 does not pretend that several
owner actions form one durable snapshot transaction.

## Service and status integration

The exact query is part of the existing mutex-linearized history action:

- identical pending work coalesces by generation;
- a different path, cursor, limit, action, or restore operation is rejected;
- drain closes admission without dropping an accepted generation;
- typed payload-store lease contention retains the request for bounded retry;
- typed integrity failure enters the existing fail-closed integrity path; and
- ordinary query/cursor failures complete as operator-visible failures without
  terminating the daemon.

`anonsync.peer-service.status.v12` renders the retained query beside requested,
started, and completed generations, the bounded inventory or restore result,
last failure, retry delay, and saturating counters. Live and terminal status
share one renderer. Status reads only cached owner state; it never opens the
payload store or traverses the replica model.

## Exact path and cursor validation

A query path must pass the same canonical relative-path grammar as synced
operations and is independently capped at 4,096 bytes so the local frame stays
bounded. A cursor must be one lowercase SHA-256 operation ID. The owner then
revalidates semantic membership against the current replica snapshot:

- absent or inactive operation: reject;
- tombstone cursor: reject;
- currently visible operation: reject;
- operation outside the selected path: reject; and
- active superseded file in scope: use its canonical sort tuple as the exclusive
  lower bound.

Restore remains unchanged and re-proves every load-bearing owner from scratch.
An inventory cursor, page, payload-presence bit, or status generation cannot
authorize filesystem publication.

## Mechanical regressions

The focused suites prove:

- default query compatibility and the 1..1,024 hard limit;
- exact one-entry first and second pages with no omission or duplication;
- path-scoped complete history and an empty absent-path result;
- rejection of malformed paths, malformed cursors, visible cursors, and cursors
  from another path scope;
- strict lowercase-hex path framing, canonical decimal limits, PID binding,
  exact response echo, same-query coalescing, changed-query rejection, action
  completion, and post-drain rejection;
- a 512-path borrowed visitor in exact bytewise order with model-owned pointer
  identity;
- optimized causal coverage equal to pairwise supersession over 258 active
  operations; and
- one real two-peer process performing path-scoped v1 discovery, rooted restore,
  a truncated one-entry page over the resulting two predecessors, exact second-
  page continuation, and four generation-accounted owner actions in one PID.

## Contamination correction

The working cube contained an unsealed protocol-generation-3 implementation,
tests, and prose that allowed superseded file operations to reconcile without
payload bytes. The branch failed the existing operation-before-bytes safety bar:
operation-ID page order can make a metadata-only predecessor temporarily
visible after a partial pull, and a crash can preserve that state even though
the source later considers the operation historical and has no obligation to
resend its payload.

The protocol, reconciliation service, SQLite-owner extension, regressions, and
associated prose were restored byte-for-byte from a newly extracted sealed
rev0966 parent. Rev0967 retains reconciliation protocol generation 2. A future
metadata-only history design needs durable staging or a causally safe transfer
order before it may weaken the payload requirement.

## Complexity and remaining waste

For A active operations, C causal-context entries, H selected historical file
operations, and page size K:

- grouped model traversal: O(A log A) sort and O(A) pointers;
- deterministic visible projection: O(C log D) causal aggregation for D
  distinct actors, plus work bounded by the O(A log A) pointer/visible-ID
  ordering;
- page selection: O(H log K) and O(K) response objects;
- exact path lookup: one O(A) active scan plus the selected path's causal and
  visible-ID work, still without a durable per-path index;
- payload presence: one complete payload-store namespace snapshot per explicit
  inspection; and
- ordinary status: O(cached status size), with no filesystem or causal scan.

The larger durable evidence pager and payload namespace are still complete-scan
owners. A later schema migration may add durable sequence indexes, but this
revision deliberately does not create a parallel cache with independent
correctness semantics.

## Callback-boundary audit correction

A registered whole-source callback inventory rejected the initial grouped
visitor because it added a new `std::function` occurrence to the model API.
The final implementation retains the same one-pass borrowed projection but
uses a compile-time visitor and private value-returning helpers. This avoids a
new type-erased executable boundary and keeps the pre-existing reviewed
callback inventory exact.

## What this proves

Rev0967 proves that every active superseded file operation can be reached through
bounded deterministic owner requests; that page identity is explicit and
fail-closed under stale cursors; that path-scoped browsing survives the real
service/action/status pipeline; and that the shared visible projection no longer
repeats whole-model and all-pairs work for each candidate.

## What this does not prove

This revision does not make history chronological, stable across concurrent
multi-page mutations, deliberately retained, quota-bound, garbage-collected, or
friendly to nontechnical users. It does not add version pinning, Archive UI,
conflict browsing, batch restore, directory restore, rename identity, block
delta transfer, cross-platform metadata recovery, or cross-owner transaction
atomicity. Historical bytes remain available only while the append-only payload
store happens to retain them.

# Revision notes — rev0967

Rev0967 makes the bounded causal-version inventory completely browsable and
removes two quadratic projection paths that made a small owner request scale
with the square of retained replica evidence.

## Mission move

Rev0966 exposed at most the first deterministic 64 predecessors by default, but
it had no path selector or continuation cursor. A share with more retained
history could therefore report `truncated=true` while leaving every later
predecessor unreachable through the shipping owner interface. The same bounded
request also called a whole-model path lookup once per active operation; a long
history at one path then performed pairwise supersession again inside each
lookup.

Rev0967 adds exact path-scoped cursor pagination through the existing owner-only
service and replaces those repeated scans with one borrowed grouped traversal
and one causal-coverage projection.

## C++ implementation

- Added `SyncReplicaHistoricalVersionQuery` with a default 64-entry limit, a
  hard 1,024-entry ceiling, an optional canonical relative path, and an optional
  exact active superseded operation cursor.
- Extended the CLI to
  `anonsync_sync versions --socket ABSOLUTE_SOCKET [--path PATH]
  [--after OPERATION_ID] [--limit 1..1024]`.
- Added the strict internal line frame
  `versions-query LIMIT PATH_HEX_OR_DASH CURSOR_OR_DASH\n`; path bytes use
  lowercase hex so whitespace and other permitted pathname bytes cannot change
  framing. Legacy `versions\n` remains the exact default query.
- Query identity participates in pending-request coalescing. A different path,
  cursor, or limit cannot overwrite an already accepted history request.
- Inspection reports both total operations in scope and operations after the
  cursor, plus `next_start_after_operation_id`. The next cursor is the exact
  operation ID at the returned page tail and exists only when another entry is
  available.
- A cursor must still name one active superseded file operation in the selected
  path scope. Missing, visible, malformed, or out-of-scope cursors fail closed.
- Advanced live and terminal status to `anonsync.peer-service.status.v12` and
  the local inspection response to
  `anonsync.local-historical-versions.response.v2`; both retain the exact query
  beside the resulting inventory or failure.

## Adjacent audit/refactor

The audit found that rev0966's nominally bounded inventory was computationally
unbounded in the wrong dimension. It iterated every active operation and called
`visible_path()` for each one, while `visible_path()` scanned every active
operation. Within one long-lived path, maximal-operation selection also compared
all candidates against all candidates.

`SyncReplicaModel::for_each_active_path()` now sorts one vector of borrowed
operation pointers by path and operation ID, presents one immutable span per
path, and computes that path's view once. The visible-set implementation
aggregates the greatest causal-context counter per actor and then tests each dot
once. A differential regression compares the optimized result with the public
pairwise supersession predicate across a 258-operation concurrent history.
`visible_paths()` and history inspection both consume the grouped visitor.

The run also audited and removed an unsealed protocol-generation-3 branch that
allowed superseded file operations to cross reconciliation without bytes. In
operation-ID page order, a metadata-only predecessor could become temporarily
visible after a partial pull and survive a crash with no source obligation to
resend its payload. The protocol, service, SQLite-owner, tests, and prose were
restored byte-for-byte from a newly extracted sealed rev0966 parent. Rev0967
retains protocol generation 2 and its operation-before-bytes invariant.

## Registered callback-boundary correction

The complete registry caught that the first grouped-path implementation had
introduced `std::function` into the public model surface. That would have made
type-erased executable ownership part of a causal projection API merely to
avoid repeated scans. Rev0967 now keeps the synchronous borrowed visitor as a
compile-time template and moves sorting plus candidate projection behind two
non-executable private helpers. The exact callback inventory therefore remains
unchanged from the sealed parent.

## Mechanical validation

```text
Exact rev0967 source passed the complete GCC 14.2 Debug graph (527/527 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 386 folder-owner, 7 folder-process, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 113 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 227/227 checks. A fresh Clang 17 Debug product dependency graph completed 238/238 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error, including the 386-check folder-owner suite in 18.72 seconds at 1,347,424 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic.
```

## Complexity boundary

For A active operations, C retained causal-context entries, H historical file
operations in the selected scope, and K requested entries:

- global grouping retains O(A) borrowed pointers and sorts them in O(A log A);
- deterministic causal coverage costs O(C log D), with D distinct actors in a
  path, while the grouped pointer sort and visible-ID ordering remain within
  O(A log A);
- bounded history selection retains O(K) response entries and costs
  O(H log K);
- an exact path query still scans the immutable model but avoids whole-model
  response clones; and
- explicit inspection still performs one complete payload-store snapshot to
  report exact payload presence.

Ordinary status remains filesystem-cold and causal-model-cold.

## Nonclaims

Cursor pages are separate observations, not one durable multi-page transaction.
Each inventory carries its source replica generation, visible-state digest, and
payload-snapshot digest; an operator or future UI must restart pagination when
those cutpoints differ. This revision does not add wall-clock chronology,
retention policy, pins, quotas, garbage collection, Archive UX, batch or
directory restore, conflict resolution, rename identity, or cross-owner
filesystem/SQLite atomicity. Restore still succeeds only while the exact
historical payload remains retained.

See `PAGED_CAUSAL_VERSION_QUERY_AND_GROUPED_PROJECTION_AUDIT_rev0967.md`.

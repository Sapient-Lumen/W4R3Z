# Bounded historical status page and single-result audit — rev0971

## Mission relevance

AnonSync exists to replace Resilio Sync with one practical C++ folder-sync
product. Rev0966–rev0970 made retained causal predecessors inspectable,
paginated, source-bound, safely restorable, and optionally payload-cold. Those
semantics were useful, but the owner-control transport still had a composition
error: the query accepted a page that the same daemon was not guaranteed to be
able to publish through its status socket.

A recovery browser is not usable when a valid large page can terminate or stall
the service while trying to report success. Rev0971 makes the status envelope a
first-class bounded product contract without changing causal ordering, source
cutpoints, restore authority, or reconciliation generation 2.

## Defect found

The strict local status socket rejects JSON objects larger than 1 MiB. History
inspection nevertheless accepted as many as 1,024 entries, and each entry can
carry a canonical path of up to 4,096 bytes. JSON escaping can expand an input
byte to six output bytes. A valid accepted query could therefore produce many
megabytes of status JSON even before ordinary service health, route, retry, and
failure fields were added.

The completed inventory was also retained twice in one status document:

1. `historical_versions.last_inventory`, the stable owner result; and
2. `last_step.historical_version_inventory`, a generic transient step copy.

That duplication was unnecessary and could almost double the largest status
object. It also made generic last-step replacement semantics look like a second
history-result authority even though every shipping client already waits on the
stable `historical_versions` domain.

## One exact byte frontier

The folder owner still computes the same causally ordered, entry-count-bounded
page. Before the peer service retains that page for status publication,
`bound_sync_replica_historical_version_inventory_for_status_or_throw()` applies
one additional deterministic prefix frontier.

The frontier:

- uses the exact canonical inventory JSON encoder, not an approximate second
  serializer;
- counts bytes with a non-allocating stream buffer before emitting JSON;
- keeps the largest prefix whose inventory encoding is at most 256 KiB;
- always retains at least one entry when the owner returned entries;
- never claims a byte stop unless at least one entry was actually omitted;
- preserves total source counts, query identity, source cutpoint, and canonical
  order; and
- names the retained tail as the ordinary `next_start_after_operation_id`.

The byte budget is one quarter of the fixed 1 MiB socket response envelope. The
remaining three quarters are reserved for the rest of the service status,
including configuration identity, route state, counters, scrub and quarantine
health, failures, and lifecycle evidence. The byte budget is deliberately an
internal presentation invariant rather than a user-controlled scheduler knob.

## Stop reasons remain distinct

`SyncReplicaHistoricalVersionInventory` now reports:

- `entry_limit_frontier_reached`: the folder owner found more causal entries
  than the query's `maximum_entries`;
- `status_byte_limit`: the service's fixed encoded inventory budget; and
- `status_byte_frontier_reached`: the transport retained a strict prefix to stay
  inside that budget.

`truncated` is true when either frontier is reached. Both use the same exact
operation-ID cursor, so existing pagination continues without a parallel token,
page numbering scheme, or mutable server-side session. A page can truthfully
report both reasons when a very large count-bounded page also exceeds the byte
budget.

## Canonical encoder refactor

History query and inventory JSON moved into
`sync_replica_historical_version_inventory_json.cpp`. The same implementation
is used by:

1. the exact byte-counting pass that selects a prefix; and
2. the live and terminal status renderer that emits the retained inventory.

This removes a class of size-accounting drift in which counting and emission
escape strings differently or add fields independently. Counting uses a custom
`std::streambuf` and therefore does not allocate a speculative multi-megabyte
JSON string merely to learn that it must be truncated. The shipping status
renderer invokes the stream form directly, so extraction of the canonical module
does not introduce a second accepted-inventory JSON temporary.

## Single stable result

`account_sync_replica_peer_service_step()` still retains generation, action,
request, and typed failure correlation in generic `last_step`, but clears the
completed inventory from that copied step. The one durable-in-process result is
`historical_versions.last_inventory`. A later network or repair step may replace
`last_step` without affecting the stable history result, exactly as existing
shipping clients already assume.

The direct C++ step result remains available to the owner-thread caller before
accounting. This refactor changes presentation retention, not execution or
restore semantics.

## Complexity

Let `n <= 1,024` be the count-bounded owner page and `b` its encoded size.
Canonical size counting is O(n + b) with O(1) auxiliary counting storage. If the
page exceeds the limit, a binary search performs O(log n) counting passes over
prefixes. Since `n` is fixed and small, the worst case remains bounded; no pass
allocates the rejected JSON. The final status allocates only the accepted
inventory, at most 256 KiB.

The owner still retains O(n) C++ entry objects before the presentation frontier.
Rev0971 does not claim to make causal projection itself byte-streaming or to add
history retention and garbage collection.

## Tests and mechanical authority

The local-control regression synthesizes the maximum accepted 1,024-entry page
with 4,096-byte paths and proves:

- the unbounded canonical JSON exceeds the new inventory budget;
- the service boundary retains a non-empty strict prefix;
- the prefix is byte-for-byte the beginning of the canonical owner order;
- the next cursor names the exact retained tail;
- entry and byte stop reasons remain independent;
- the final canonical inventory is at most 256 KiB and below the 1 MiB socket
  cap; and
- generic `last_step` retains action correlation but no duplicate inventory.

The configured real-service oracle requires the new fields on exact and
metadata pages, checks their count/frontier coherence, and rejects a matching
transient step that duplicates the stable completed inventory. Direct and I2P
status readers advance with the same schema.

The structural audit binds the fixed budgets, canonical counting/emission
module, service cutpoint, independent stop reasons, single-copy accounting,
focused regression, process oracle, documentation, and release policy.

## Research and design context

RFC 8259 permits control characters to be represented with six-byte `\\u00XX`
escapes. That makes character count an unsafe proxy for the byte size of a JSON
status object. Rev0971 therefore measures the exact emitted encoding rather
than multiplying path lengths by a guessed factor.

Cursor pagination remains preferable to mutable offset pagination here because
the existing source cutpoint binds the immutable operation set and the cursor
names an exact causal operation. The new frontier does not introduce a hidden
server session whose lifetime or restart behavior would need separate
persistence.

## What this proves

Rev0971 proves that every history inventory retained by the shipping peer
service has a deterministic encoded prefix within a fixed sub-budget of the
local status transport, and that the completed page appears once in stable
status rather than twice.

It does not prove a global maximum for arbitrary future status fields without
maintaining their own bounds. The local socket's final 1 MiB validation remains
the terminal guard, and the structural test keeps the inventory budget strictly
below it.

## What remains

This revision does not add retention windows, pins, reachability collection,
garbage collection, remote transfer of superseded operations, chronological
ordering, conflict-copy UX, batch restore, directory restore, selective sync,
placeholders, or a graphical browser. Those remain the larger history lifecycle
and Resilio-replacement product edges.

Exact rev0971 source passed the clean GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 406 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 132 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 267/267 checks. A clean-root Clang 17 Debug product dependency graph completed 239/239 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 406-check folder-owner suite in 18.93 seconds at 1,371,184 KiB peak RSS and the 132-check local-control suite in 0.57 seconds. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0970 parent SHA-256 matched 57cb832afa5b63c3b7ab63028873855ec18c6e2ec90059c7ac7b64200ba2e7d7 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 13/13 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,058,026 bytes with SHA-256 11b2a46a3fc169546819c71172347dc64bb6f05bbca16d58ff5a790d21e239a8.

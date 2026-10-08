# Explicit causal-version inspection and rooted restore audit — rev0966

## Heart of the mission

AnonSync exists to replace Resilio Sync with one usable C++ folder-sync
application. A replacement must let an owner recover an earlier file value
without leaving the running service, manually spelunking a private payload
namespace, or starting a second synchronization engine. The recovery path must
reuse the same authenticated causal model, rooted filesystem authority, atomic
publisher, durable catalog, and ordinary peer convergence as every other local
change.

Rev0966 is the first deliberately narrow product slice toward ordinary version
recovery. It exposes retained causal predecessors that already exist in the
replica graph and whose immutable payload bytes still exist in the append-only
payload store. It can publish one exact selected predecessor as a new local
causal successor. It does not claim a retention policy, wall-clock history,
version labels, automatic pruning, garbage collection, conflict resolution, or
a graphical Archive browser.

## The operability gap

Before rev0966, AnonSync retained immutable superseded file operations and their
content-addressed payloads, but that evidence was not an owner-operable recovery
surface. The low-level model could prove old values existed, yet the shipping
service offered no bounded command to discover them and no reviewed route to
restore one through the ordinary rooted folder owner. Recovering bytes therefore
required private-database knowledge or an unreviewed prototype, neither of
which is acceptable replacement-product behavior.

The discarded retained-version prototype found during rev0965 was not imported.
It widened the low-level CLI, duplicated ownership, and had not been validated
against the current service, action-linearization, integrity, and rooted
publication boundaries. Rev0966 instead builds a vertical slice through the
retained linked-peer service.

## Product boundary

The owner-only local interface adds two explicit commands:

```text
anonsync_sync versions --socket ABSOLUTE_SOCKET
anonsync_sync restore --socket ABSOLUTE_SOCKET --operation LOWERCASE_SHA256
```

`versions` schedules one potentially expensive inspection and returns only
request admission. The completed bounded inventory appears in ordinary service
status. `restore` schedules one exact operation ID and likewise reports
completion through status. Both commands use the existing private mode-0600
Unix socket, strict line framing, peer-process PID binding, one mutex-linearized
action snapshot, monotonic generations, request coalescing, and the existing
drain seal.

This is intentionally not a generic command dispatcher. Historical inspection
and restore occupy one dedicated pending lane. An identical pending request can
coalesce; a different history request is rejected until the prior generation is
complete. Requests serialized after drain are rejected without advancing the
generation.

## What an inventory entry means

An inventory entry is one active immutable file operation that is not currently
a visible head at its canonical path. Its actor epoch and counter are causal
identity, not a wall-clock date. The projection reports:

- operation ID, canonical path, exact size and SHA-256;
- actor identity and causal counter;
- the current primary operation and visible-head count;
- whether the exact payload is present; and
- whether the candidate is immediately restore-ready.

Restore-ready means only that the exact payload is present, the current path has
one unambiguous visible head, and the candidate differs from the currently
materialized value. The status object is advisory inspection evidence. Restore
re-proves all load-bearing state rather than trusting the earlier projection.

## Explicit inspection, not status-time traversal

Ordinary status rendering remains filesystem-cold. It never walks the payload
namespace or causal graph. The explicit owner action pays for exactly one
complete rooted payload-store snapshot and one immutable replica snapshot. The
result records the source replica generation, visible-state digest, payload
snapshot digest, and exact hashed/reused byte accounting.

The default response retains at most 64 entries; the hard API ceiling is 1,024.
Counts cover every active superseded file operation even when the returned list
is truncated. Ordering is deterministic by canonical path, actor device, actor
epoch, descending causal counter, then operation ID.

## Adjacent projection refactor

The first implementation restored the full causal model, cloned every active
operation into `all_operations()`, cloned every visible path through
`visible_paths()`, sorted the complete operation vector, and only then returned
a 64-entry diagnostic result. That turned a bounded operator response into
avoidable O(active operations) duplicate storage.

Rev0966 adds a borrowed immutable `for_each_active_operation` visitor to the
model. Inspection asks `visible_path` only for the operation being considered
and maintains a bounded max-heap whose root is the worst retained candidate.
The heap never exceeds the requested entry count; `std::sort_heap` produces the
same canonical final order. The complete restored model remains necessary for
causal interpretation, and the complete payload snapshot remains necessary for
exact payload-presence authority, but the projection no longer creates two
additional whole-model containers.

The visitor is deliberately narrow: the callback may not mutate the model or
retain references beyond the call. Missing active evidence is treated as an
internal consistency failure.

## Exact restore authority path

Restore accepts only one lowercase SHA-256 operation ID. The folder owner then:

1. snapshots and restores the current replica model;
2. requires the selected operation to be an active file operation that is not
   already visible;
3. requires exactly one current visible head and rejects unresolved conflicts;
4. rejects a candidate whose bytes equal the current file value;
5. requires the durable catalog entry to match the exact current visible head;
6. descriptor-roots and re-observes the current path, including absence for a
   tombstoned head;
7. opens the selected immutable payload through exact targeted payload-store
   access;
8. acquires the SQLite visible-projection guard at the previously observed
   digest and re-proves the historical operation, current operation, and visible
   head set;
9. re-proves the catalog and current rooted path immediately before mutation;
10. publishes the selected bytes through the existing atomic replace-or-create
    helper using the already-opened payload descriptor;
11. re-observes exact published bytes and commits the projection guard; and
12. invokes the ordinary prepared local-file scanner, which mints or adopts a
    new causal successor under the existing actor, catalog, and observed-head
    cutpoints.

The returned successor must differ from both the selected historical operation
and the replaced visible operation, contain the exact selected bytes, and
causally supersede the replaced head. The old operations remain immutable
predecessors. Restore therefore creates a new present-day fact; it never
reactivates historical evidence or edits the causal past.

## Failure and crash semantics

A stale inspection cannot authorize restore. Every replica, payload, catalog,
path, and current-byte condition is checked again. Missing payload, an already
visible operation, unresolved conflict, equal current bytes, catalog drift,
filesystem drift, causal projection drift, or payload disappearance produces an
explicit operator failure while the retained daemon remains alive.

Rooted atomic publication and causal minting are not one cross-owner database
transaction. If the process dies after exact old bytes become visible but before
the new operation is committed, the ordinary scanner observes those current
bytes after restart and publishes the corresponding local change. That repair
model is preferable to a second restore journal or a second sync engine, but it
is not claimed as instantaneous atomicity across filesystem and SQLite owners.

The existing atomic publisher's recovery path remains authoritative for a
publication error that nevertheless left the exact selected bytes. It
synchronizes and re-proves the file and parent before the ordinary scanner is
allowed to mint the successor.

## Service scheduling and status v11

The linked-peer owner treats history work as one bounded operator action. Typed
payload-integrity failure and typed payload-store lease contention retain their
existing fail-closed/retry behavior. Other runtime errors complete the request
as an explicit `last_failure`; they do not terminate the daemon or silently
retry a stale operation forever.

`anonsync.peer-service.status.v11` reports requested, started, and completed
generations; pending action and operation ID; retry delay; the last bounded
inventory; the last restore result; the last failure; and saturating request,
coalescing, attempt, completion, inspection, restore, and failure counters. Live
and terminal status use the same history renderer. Status itself remains a
cached owner-thread projection and performs no history inspection.

## Mechanical regressions

The focused folder-owner regression creates a file value v1, changes it to v2,
and proves that inspection returns exactly the retained v1 operation as
restore-ready. Restore must atomically publish v1, mint a third operation that
causally supersedes v2, preserve both earlier operations, and update the durable
catalog to the new successor. A later one-entry inventory proves deterministic
bounding and reports v2 as the newly superseded value. Zero, oversized, current-visible, and same-byte requests are rejected. A second fixture deletes
a cataloged file, proves the resulting tombstone causally supersedes it, reports
the old file as restore-ready behind that tombstone, and requires exact byte
recreation under a third successor.

The local-socket regression proves strict schemas and PID binding, inspection
coalescing, changed-action rejection, generation completion, future-generation
rejection, post-drain rejection, mode-0600 enforcement, and exact restore-ID
validation.

The configured real-process regression changes `alpha.txt` from v1 to v2,
waits for both authenticated services to converge, requests inspection through
the owner-only socket, selects the exact v1 operation from status, requests
restore, and then waits for both peers to converge back to v1 under a new
operation ID. It requires two requests, two attempts, two completions, one
inspection, one restore, and zero history failures.

## Audit/refactor findings

The source audit corrected two adjacent stale assumptions:

- the configured-service fixture now performs a third ordinary file overwrite
  for the history scenario, while the two deliberate corrupt-payload mutations
  remain fenced through the exact reader identity lease; and
- the sealed rev0963 record remains bound to status v10 rather than being
  accidentally rewritten by the current v11 schema migration.

The review also rejected query-time payload traversal, a second history daemon,
a low-level private-database restore command, whole-model response clones, and
an implicit promise that append-only retention is permanent user history.

## Complexity and remaining waste

Inspection still restores the complete causal model and completes a full
payload-store namespace observation. Its additional retained response storage
is O(requested entries), with K equal to the explicit requested limit, but runtime remains O(active
operations plus payload namespace). This is acceptable for an explicit owner
action and not for polling status.

The append-only payload store has no reachability collector. Consequently,
older bytes may remain available for a long time, but availability is accidental
until a retention contract exists. Conversely, any future collector could make
an old operation non-restorable unless it pins user versions explicitly.
Inventory has causal ordering fields but no trustworthy wall-clock chronology.
The owner-only JSON interface is operable but not yet ordinary desktop recovery
UX.

## What this proves

Rev0966 proves that the retained service can:

- discover a deterministic bounded set of active superseded file values;
- distinguish causal evidence from currently retained payload bytes;
- keep ordinary status filesystem-cold;
- restore one exact unambiguous value through rooted atomic publication;
- mint a new causal successor through the ordinary local scanner;
- converge that restored value to an authenticated peer; and
- keep inspection/restore linearized with local drain and other owner actions.

## What this does not prove

This revision does not provide time-based or count-based retention, reachability
pins, quotas, garbage collection, Archive browsing, friendly timestamps,
version labels, batch restore, directory restore, rename identity, conflict
resolution, selective synchronization, cross-platform metadata recovery,
malicious same-UID defense, or a graphical interface. It does not guarantee
that every old operation remains restorable. It does not make the filesystem
publication and replica mutation one atomic transaction. Those are the next
product boundaries, not hidden implications of an append-only store.

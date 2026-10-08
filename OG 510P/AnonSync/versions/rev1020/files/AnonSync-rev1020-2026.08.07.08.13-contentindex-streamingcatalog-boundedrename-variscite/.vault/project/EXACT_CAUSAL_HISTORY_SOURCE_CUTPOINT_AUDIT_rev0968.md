# Exact causal-history source cutpoint audit — rev0968

## Mission relevance

AnonSync exists to replace Resilio Sync with one usable C++ synchronization
product. Rev0966 made retained causal predecessors inspectable and restorable;
rev0967 made that inventory reachable through bounded pages. A recovery browser
cannot be trustworthy, however, if page two can silently come from a different
causal and payload source than page one. Rev0968 closes that browse-consistency
hole before adding retention policy or garbage collection.

This is not a second history database and not a long-lived database snapshot.
It is a compact fail-closed token over the exact immutable inputs that determine
one page.

## Defect found

Rev0967 exposed three source diagnostics on each page: replica state generation,
visible-state digest, and payload-snapshot digest. A caller could compare them
after receiving several pages, but the service did not accept those diagnostics
as an authority-bearing continuation input. That left several concrete failure
modes:

1. an unrelated operation could be inserted before or after the page cursor;
2. a historical operation could become visible, disappear from the active set,
   or move relative to the cursor;
3. retained payload availability could change between pages; and
4. callers could accidentally combine pages first and discover the mismatch
   only later, or not compare the diagnostics at all.

The rev0967 cursor guarded only the selected tail operation. It could reject a
missing, visible, malformed, or out-of-path cursor, but it did not bind the rest
of the active causal model or retained payload namespace.

## Source-cutpoint contract

One source cutpoint contains exactly two lowercase SHA-256 digests:

```text
operation_set_digest
payload_snapshot_digest
```

The canonical owner token is:

```text
v1:<64 lowercase operation-set hex>:<64 lowercase payload-snapshot hex>
```

The framing is fixed at 132 bytes. Unknown versions, wrong separators, wrong
lengths, uppercase hex, and malformed digests fail before action admission.
The token can be copied from `source_cutpoint` in a first-page inventory into:

```text
anonsync_sync versions ... --source-cutpoint TOKEN
```

or into the fourth field of the strict local socket frame:

```text
versions-query LIMIT PATH_HEX_OR_DASH CURSOR_OR_DASH SOURCE_OR_DASH\n
```

The server still accepts rev0967's three-field query frame and the original
`versions\n` default request. New responses use
`anonsync.local-historical-versions.response.v3` and echo the exact expected
source cutpoint or null.

## Why these two digests

The active operation-set digest binds every active immutable causal operation,
including operations unrelated to the selected path. That broad binding avoids
subtle insertion and visibility omissions without adding a second per-path
index or inventing new query-specific digest semantics.

The payload-snapshot digest binds exact retained payload identities and sizes as
observed by the existing complete rooted payload-store snapshot. Historical
entries are returned with payload-presence and restore-readiness fields, so
retained-byte availability is part of page identity rather than incidental
status.

The token deliberately does not bind replica `state_generation`. That counter
also advances for liveness and other state not used to compute a historical
page. Binding it would manufacture failures when the causal model and payload
namespace were unchanged. `source_replica_state_generation` and
`source_visible_state_digest` remain useful diagnostics, but the exact
operation-set digest is the causal browse authority.

## Observation order and wasted-work correction

Bound continuation inspection now follows this order:

1. validate the complete query and canonical token;
2. take the first immutable replica snapshot;
3. compare the expected operation-set digest;
4. restore the model and validate the cursor against that exact model;
5. take one complete rooted payload-store snapshot;
6. take a second immutable replica snapshot;
7. require the operation-set digest to be unchanged;
8. compare the expected payload-snapshot digest; and
9. project and return the bounded inventory.

The first operation-set comparison and cursor validation happen before the
complete payload observation. A stale page source or stale cursor therefore
cannot force an avoidable O(payload namespace) scan. The second replica
snapshot brackets that expensive observation, preventing one returned page
from combining a causal projection with bytes observed across an intervening
active-operation change.

A separate cross-owner transaction is not claimed. SQLite read transactions
provide stable snapshots within one database connection, but the payload store
is a distinct rooted owner. The explicit bracket and digests are the narrow
composition contract used here.

## Typed source drift

Source drift is not parsed from prose. The folder owner throws a dedicated
`SyncReplicaHistoricalVersionSourceChangedError` with one exact stage:

- `operation_set_before_payload_observation`;
- `operation_set_during_payload_observation`; or
- `payload_snapshot`.

The peer service classifies it as `source_changed`, clears stale inventory and
restore results, increments the existing historical failure counter, and keeps
the daemon alive. Ordinary query or restore failures remain `operation_failed`.
Live and terminal `anonsync.peer-service.status.v13` expose the stable retained
`last_failure_class` / `last_source_change_stage` pair. The exact history step
also serializes the same class and stage when it is the current generic
`last_step`; a later network step may legitimately replace that transient view.
An adjacent audit found that the first implementation populated the per-step
fields but never serialized them; rev0968 removes that dead diagnostic path
without pretending `last_step` is retained history. Status remains
filesystem-cold.

No replacement token is fabricated on failure. In particular, an early
operation-set mismatch has intentionally not observed the payload namespace.
The operator must restart pagination to obtain a new first-page cutpoint.

## Tests and mechanical authority

The focused folder-owner regression proves:

- canonical source-token round-trip and malformed framing rejection;
- a second page bound to the exact first-page operation set and payload
  snapshot;
- fail-closed payload-snapshot drift after an unreferenced payload is retained;
- fail-closed pre-scan operation-set drift after a new causal successor; and
- exact typed failure stages.

The local-socket regression proves v3 response shape, exact token echo,
three-field backward compatibility, malformed-token rejection, query-identity
coalescing, pending-action preservation, PID binding, mode checks, and drain
serialization. The real configured-service process regression carries a first
page's source token into the second owner request, then publishes an unrelated
path whose active operation changes the broad causal source. Reusing the old
token must complete as `source_changed` at
`operation_set_before_payload_observation`, clear stale result objects, retain
the same daemon PID, and increment the ordinary failed-action accounting.

The structural audit additionally binds source order: the early operation-set
comparison and cursor validation must precede `payload_store->snapshot_or_throw`,
and the second operation-set comparison plus payload-token comparison must
follow it. It also rejects a generic state-generation comparison at that
cutpoint.

## Complexity and boundaries

The source token is constant size. A valid bound continuation adds two digest
comparisons and one second replica snapshot around work rev0967 already paid.
An invalid operation-set token or invalid cursor fails before the complete
payload scan. Projection complexity remains the rev0967 grouped-model and
bounded-heap design.

The operation-set digest is cryptographic collision authority in the same sense
as the operation and payload digests already used by AnonSync. This revision
does not add a chronology clock, durable UI session, database read lease, or
cross-process snapshot handle.

## Research context

Syncthing's official Block Exchange Protocol uses an index ID and maximum
sequence tuple to identify a retained index point and requires ordered updates
for reliable continuation. That is useful precedent for making continuation
source identity explicit, although AnonSync's token binds different local owner
inputs and is not wire compatible:

- https://docs.syncthing.net/specs/bep-v1.html

SQLite documents that one read transaction continues to observe its historic
snapshot while other connections commit changes. Rev0968 uses each replica
snapshot as an immutable observation but does not stretch one SQLite transaction
across the distinct payload owner:

- https://sqlite.org/lang_transaction.html

## What this proves

Rev0968 proves that a caller can bind every later bounded causal-history page to
the exact active operation set and retained payload snapshot returned by the
first page. A mismatch fails as a typed owner-visible action, and stale causal
sources or cursors are rejected before avoidable payload-namespace work.

## What this does not prove

This is not durable version pinning, deliberate retention, a quota, garbage
collection, chronology, conflict UI, Archive browsing, batch restore, directory
restore, or a cross-owner atomic snapshot. A valid source cutpoint preserves
browse consistency only while its exact operation and payload digests still
match. Restore continues to re-prove the current replica, catalog, payload, and
rooted filesystem owners from scratch.

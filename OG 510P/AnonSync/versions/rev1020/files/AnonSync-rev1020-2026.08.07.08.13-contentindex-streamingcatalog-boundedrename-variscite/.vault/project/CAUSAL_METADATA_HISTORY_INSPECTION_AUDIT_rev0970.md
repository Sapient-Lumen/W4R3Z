# Causal-metadata history inspection audit — rev0970

## Mission relevance

AnonSync exists to replace Resilio Sync with one usable C++ folder-sync
product. Rev0966–rev0969 made retained causal predecessors inspectable,
paginated, source-bound, and safely restorable against the exact current head.
That recovery seam was correct but needlessly expensive for ordinary browsing:
every `versions` request, including a one-entry page for one path, observed the
complete private payload namespace before returning causal metadata.

A history browser must be able to list what the causal model knows without
pretending that it has proved which immutable payload objects are currently
present. Rev0970 adds that explicit lower-authority mode while preserving the
existing exact mode unchanged.

## Defect found

Before rev0970, the only history inspection contract was exact payload
availability. One request therefore performed all of the following even when a
caller wanted only operation IDs, paths, sizes, content digests, actor dots, and
current-head identities:

1. snapshot the complete replica operation set;
2. restore and project the causal model;
3. acquire the payload-store observation authority;
4. enumerate and re-prove the complete private payload namespace;
5. bracket that payload observation with a second replica snapshot; and
6. report per-entry payload presence and restore readiness.

The work was independent of page size and selected path. A 1-entry path-scoped
page over a large append-only store could therefore pay O(retained payload
namespace) I/O. More seriously, callers had no truthful way to request a cheap
causal listing: replacing `false` or zero for unobserved payload facts would
have turned absence of proof into negative proof.

## Two explicit inspection authorities

`SyncReplicaHistoricalVersionInspectionMode` is the shared authority selector:

- `ExactPayloadAvailability` / JSON `exact_payload_availability` is the existing
  behavior. It observes the complete payload store, brackets that observation
  with the operation-set owner, and reports exact payload-presence and
  restore-readiness evidence.
- `CausalMetadataOnly` / JSON `causal_metadata_only` observes only the immutable
  replica snapshot and causal model. It never calls the payload-store owner and
  reports every payload-derived field as unknown.

The shipping command is:

```text
anonsync_sync versions --socket ABSOLUTE_SOCKET \
    --inspection-mode exact|metadata \
    [--path CANONICAL_RELATIVE_PATH] [--limit 1..1024] \
    [--after OPERATION_SHA256] [--source-cutpoint TOKEN]
```

The default remains `exact`, preserving existing CLI behavior.

## Unknown is not false

Metadata-only pages still report causal facts proved by the replica snapshot:

- operation ID;
- canonical path;
- immutable size and content SHA-256 declared by that operation;
- actor device, epoch, and counter;
- visible-head count;
- current primary operation ID and kind;
- operation-set and visible-state digests; and
- pagination counts and cursor.

They serialize the following payload-derived values as JSON `null`:

- `source_payload_snapshot_digest`;
- payload scan hashed/reused entry and byte counts;
- aggregate payload-present and restore-ready counts; and
- each entry's `payload_present` and `restore_ready` values.

The C++ representation uses `std::optional`, so a future renderer cannot
silently collapse “not observed” into `false` or zero. A metadata page is useful
for browsing and selection, but it is not evidence that bytes are missing or
that a restore can proceed. Restore continues to re-prove payload and rooted
filesystem authority from scratch.

## Mode-bound source cutpoints

Exact pages preserve the rev0968 token byte-for-byte:

```text
v1:<operation-set SHA-256>:<payload-snapshot SHA-256>
```

Metadata-only pages use:

```text
v2:metadata:<operation-set SHA-256>
```

The metadata token carries no placeholder payload digest. The query validates
that a supplied cutpoint has the same inspection mode, so an exact page cannot
silently continue from a causal-only token and a metadata page cannot inherit
an old payload proof. Both tokens bind the complete active operation set. Only
exact v1 additionally binds the retained payload snapshot.

The existing `operation_set_before_payload_observation` source-change stage is
retained for protocol compatibility. Its comparison occurs before the
mode-specific branch; for metadata mode it therefore fails before projection
and, trivially, before any payload observation that the mode would otherwise
skip.

## Local protocol and status

The strict owner-only query frame is now:

```text
versions-query MODE LIMIT PATH_HEX_OR_DASH CURSOR_OR_DASH SOURCE_OR_DASH\n
```

`MODE` is the canonical long name. The original `versions\n`, rev0967
three-field frame, and rev0968 four-field frame remain accepted as exact-mode
compatibility requests. New clients send all five fields.

The PID-bound local response advances to
`anonsync.local-historical-versions.response.v4` and echoes the canonical mode.
Live and terminal service reporting advances to
`anonsync.peer-service.status.v15`. Query identity includes mode, preventing an
exact request from coalescing with a metadata-only request that has the same
path, limit, cursor, and source token.

## Adjacent audit and refactor

The first implementation risk was authority vocabulary drifting among CLI
parsing, socket framing, service coalescing, source-token encoding, and JSON
rendering. Rev0970 centralizes canonical mode names and parsing beside the
shared query and cutpoint types. Every surface consumes that one vocabulary.

The second risk was keeping scalar booleans and counters while adding a mode
that did not observe them. Rev0970 changes the inventory boundary itself to
optional payload evidence instead of relying on renderer conventions. The
status renderer has canonical optional-boolean and optional-counter paths, so
both live and terminal output preserve the same distinction.

The optional-type refactor exposed one stale test oracle in the adjacent
restore regression: boolean context on `std::optional<bool>` tests engagement,
not the contained value. The old assertion could therefore accept an engaged
`false`. Rev0970 now compares both exact-mode fields with
`std::optional<bool>(true)`, preserving the regression's original semantic
claim rather than merely proving that an observation occurred.

The audit deliberately rejected two tempting alternatives:

1. **Report `false` and zero in metadata mode.** That would make unobserved
   payload availability indistinguishable from exact absence.
2. **Use targeted payload opens for exact mode in this revision.** A targeted
   probe could answer selected entries cheaply, but it would not preserve the
   existing exact page's complete namespace-health, capacity, unexpected-entry,
   and snapshot-digest authority. That optimization needs a separately named
   contract rather than weakening v1.

## Complexity

For a selected path, metadata-only inspection still restores the immutable
replica model and scans active operations for that path under the current model
API. It retains at most the requested page plus the model snapshot. It performs
zero payload-store lease acquisitions, directory enumerations, opens, reads,
or hashes.

Exact mode retains the rev0969 cost and authority: one complete payload-store
snapshot bracketed by replica operation-set observations. Rev0970 does not
claim to make exact availability proportional to page size.

## Tests and mechanical authority

The focused folder-owner regression creates one superseded operation, inserts
an unexpected entry into the private payload namespace, and proves:

- metadata-only inspection succeeds while the exact inspection fails;
- every payload-derived metadata field is disengaged;
- no payload scan diagnostics are manufactured;
- the v2 metadata token round-trips and pins a repeated page;
- an exact v1 token cannot be used by a metadata query; and
- after the unexpected entry is removed, exact mode still reports exact payload
  presence and restore readiness.

The local-socket regression proves v4 response shape, canonical mode framing,
mode-preserving action identity, v2 token echo, legacy exact-frame
compatibility, and rejection of a metadata token on an implicit exact frame.
The configured two-peer service regression exercises the shipping
`--inspection-mode metadata` command, validates v15 stable status, requires
null payload evidence, and accounts for the additional completed inspection.
The route-status oracle moves with the same v15 schema.

The structural audit binds the no-payload call graph, optional evidence types,
mode-specific token codec, strict local frame, CLI default, status schemas,
focused regressions, process oracle, documentation, and release policy.

## Research context

Syncthing's current documentation describes a durable index database containing
file metadata and hashes for files on disk and available from peers. That is
useful precedent for treating metadata browsing as a distinct operation from
reading file contents, although AnonSync's causal operation model and local
history API are different:

- https://docs.syncthing.net/users/config.html

Resilio's current synchronization-mode documentation makes the product value
of metadata-first browsing explicit: disconnected and selective modes can show
folders or complete file lists while real contents are absent or represented by
small placeholders. Rev0970 is not selective sync, but it follows the same
truthful separation between what can be listed and what bytes are locally
available:

- https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

## What this proves

Rev0970 proves that the owner can browse bounded causal history without
observing the payload store and without converting unknown byte availability
into negative evidence. Exact mode remains backward compatible and retains its
complete payload snapshot authority. Mode-bound tokens prevent continuation
across those two contracts.

## What this does not prove

This is not selective sync, placeholders, remote metadata transfer, deliberate
version retention, chronology, conflict UI, batch restore, directory restore,
quota enforcement, garbage collection, or a cheaper exact-availability scan.
Metadata-only output cannot authorize restore. The first real Resilio uninstall
workflow remains unnamed and unmeasured.

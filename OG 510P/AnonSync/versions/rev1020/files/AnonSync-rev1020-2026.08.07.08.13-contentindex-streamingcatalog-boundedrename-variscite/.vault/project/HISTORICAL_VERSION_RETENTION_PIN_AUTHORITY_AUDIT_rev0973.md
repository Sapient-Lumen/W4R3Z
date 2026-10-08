# Explicit historical-version retention pin authority — rev0973

## Heart of the mission

AnonSync exists to replace Resilio Sync for an ordinary person's real folders.
A retained predecessor that can be inspected and restored is not yet a usable
version lifecycle if the owner cannot say, durably and explicitly, “keep this
one.” Rev0972 measured exact retained-payload reachability but intentionally
withheld deletion authority. Rev0973 adds the first user-owned retention root
without adding a collector or a second synchronization engine.

The shipping owner commands are:

```text
anonsync_sync version-pin --socket ABSOLUTE_SOCKET \
    --operation LOWERCASE_SHA256
anonsync_sync version-unpin --socket ABSOLUTE_SOCKET \
    --operation LOWERCASE_SHA256
```

A pin names one immutable retained **File operation ID**. It does not name a
mutable path, a payload pathname, a wall-clock version, or a peer. Pin and unpin
are local storage-policy transitions. They copy no bytes, restore no path,
propagate no policy, and authorize no unlink.

## Authority placement: the replica owner, not the payload store

An unsealed donor branch stored pin markers beside immutable payload objects.
That placement was rejected. A payload object can be shared by many operations,
a pin can remain meaningful while its payload is temporarily absent, and the
historical entry shown to the user is causal replica evidence rather than a raw
byte object. A payload-side marker would therefore create two competing truths:
SQLite would own retained causal evidence while the byte namespace would own a
second, only indirectly related “history” policy.

Rev0973 gives the existing durable SQLite replica owner the only pin authority:

- schema v6 adds `sync_replica_history_pins(operation_id PRIMARY KEY)` with a
  foreign key to retained immutable operations;
- pinning requires the exact operation to exist and be a File operation;
- unpinning an absent canonical ID is idempotent, so an owner may safely retry
  after a lost response or restart;
- the canonical sorted pin set, count, and folder-bound SHA-256 digest are
  restored and re-attested with every owner snapshot; and
- an actual set transition advances the durable state generation, while an
  exact repeated transition does not.

The payload store remains a byte owner. It neither parses pin commands nor
mints policy. The local Unix-socket worker only admits and linearizes requests;
the existing peer-service owner executes them through the existing folder owner
and SQLite connection.

## Schema-v6 cutpoint and restart semantics

The current SQLite cutpoint binds the exact pin count and canonical pin-set
digest in addition to evidence, active projection, visible state, outbox, limits,
and clock policy. Restore independently loads all pin rows in strict operation-ID
order, verifies every ID, verifies the foreign operation is retained, recomputes
the count and digest, and checks the cutpoint before publication.

Migration accepts the exact prior v5 schema and seeds one empty pin set. The
migration transaction restores and attests the complete prior evidence and
outbox state before replacing only the protocol/meta surfaces, increments the
state generation once, creates the pin table, and commits one schema-v6
cutpoint. Older schema-v1 through schema-v4 sources retain their existing exact
migration paths into the same v6 surface.

Pins survive process restart because the SQLite row and redundant cutpoint are
durable. They do not depend on process-local status history, payload verification
cache, or a currently present payload object.

## History projection and exact reachability

Every metadata and exact historical inventory now includes:

- `source_historical_version_pin_set_digest`;
- `historical_version_pin_count`; and
- one exact `pinned` boolean per returned entry.

Exact mode additionally exposes `explicit_pins` in the retained-payload
reachability object. This class counts the exact File operations and distinct
`(SHA-256, declared size)` identities named by pins, including present bytes and
missing content. It is intentionally allowed to overlap current-visible,
superseded-active, and inactive-evidence classes. The existing
`retained_union` remains the deduplicated union of all retained File evidence;
a pin does not double-count a payload or make absent bytes appear present.

A pin can therefore protect an operation whose payload is currently absent.
The inventory reports that fact as a missing explicit root rather than rejecting
the policy transition or fabricating restore readiness. Ordinary authenticated
convergence remains the mechanism that may later re-admit the bytes.

Metadata-only inspection remains payload-cold. It reads the SQLite pin set as
part of the same replica snapshot but does not open the payload store, acquire a
payload lease, enumerate the payload namespace, or publish availability facts.

## Source-cutpoint evolution and legacy safety

New pages use pin-bound source tokens:

```text
v4:exact:<operation-set>:<evidence-set>:<pin-set>:<payload-snapshot>
v4:metadata:<operation-set>:<pin-set>
```

A supplied v4 token is checked against the pin-set digest before payload work.
Exact mode also brackets the complete payload observation with a second replica
snapshot and rejects pin drift during that observation. Typed stages distinguish
`historical_version_pin_set_before_payload_observation` and
`historical_version_pin_set_during_payload_observation`.

Rev0972 v3 exact, rev0968 v1 exact, and rev0970 v2 metadata tokens remain
decodable. Their missing pin field is **not** a wildcard. They are accepted only
while the current pin set is empty, then successful output upgrades to v4. A
nonempty pin set makes a pre-pin token fail at the early pin-set stage. This
preserves useful upgrade compatibility without letting later pages silently mix
retention policy while returning `pinned` entry state.

## One owner-action lane and status contract

Pin and unpin share the existing mutex-linearized historical action lane with
inspection and restore. Complete request identity includes action and operation
ID. Identical pending work coalesces by generation; a different action or ID
cannot replace pending work; a request serialized after drain is rejected
without advancing the generation.

Live and terminal service status advance to
`anonsync.peer-service.status.v18`. The historical object retains one
`last_pin_update` result with disposition, exact operation ID, resulting state
generation, pin count, and pin-set digest. Counters separately report pin and
unpin completions. The owner-only acceptance responses are:

```text
anonsync.local-historical-version-pin.response.v1
anonsync.local-historical-version-unpin.response.v1
```

They remain PID-bound, mode-0600 socket responses and report admission rather
than pretending the asynchronous durable transition already completed.

## Adjacent audit and correction

The first real configured-service proof exposed a production wiring defect.
The local socket admitted a valid pin request, but peer-service validation fell
through to the restore-request validator. Because a pin deliberately carries no
restore operation field, the daemon exited with “historical-version request
operation ID is invalid.” The corrected branch validates a restore request only
for the Restore action; Pin and Unpin are validated solely through their exact
retention operation ID. The two-peer configured-service regression now executes
pin, metadata reinspection, unpin, and reinspection in the same retained daemon.

The audit also corrected a subtler browse-consistency risk: accepting a legacy
source token as a wildcard for a nonempty pin set. Legacy tokens now retain
compatibility only for the empty set, and focused tests prove both the accepted
empty-set upgrade and early rejection after a pin exists.

A small control-path refactor centralizes the local-to-peer historical action
mapping in one exhaustive switch. Inspect, Restore, Pin, and Unpin no longer
rely on duplicated binary conditionals that could silently route a future action
through the wrong validator or counter.

The complete registry then exposed a stale structural oracle that still described
schema v5 as the destination. Following that failure uncovered a more important
gap: the shipping v5-to-v6 branch had no direct runtime fixture. The SQLite-owner
audit now follows exact schemas v1 through v6, requires pin rows during restore
and staged re-attestation, and requires every prior-version constructor branch.
A new exact v5 fixture proves migration preserves causal evidence, outbox, clock,
limits, and policy, seeds one canonical empty pin set, accepts a pin afterward,
and survives restart. A checksum-valid but wrong v5 cutpoint must fail before
schema replacement, leaving schema v5 and the absence of a pin table intact.

## Cost and remaining waste

Pin mutation loads and attests the same bounded replica snapshot already used by
other SQLite owner writes, then inserts or deletes one primary-key row and
recomputes a sorted digest over at most the retained operation ceiling. History
inspection already restores that snapshot, so entry pin state and pin-set
cutpoints add no payload scan and no second database owner.

The pin set is O(retained operations). That is safe under the existing 100,000
operation ceiling, but a future large-share profile should measure digest
recomputation and SQLite row materialization before widening that ceiling.
Incremental Merkle policy state is not justified yet; one canonical sorted set
is simpler and easier to re-attest.

## Why this is still not garbage collection

Rev0973 adds one future collection root, not deletion authority. A safe collector
must still compose at least:

- current visible and all retained causal evidence roots;
- explicit owner pins;
- prepared catalog mutations and in-flight range transfers;
- active snapshots, network reconciliation obligations, and restore work;
- per-share count/byte/age policy and a human-visible grace window;
- writer exclusion and a restart-safe mark/quarantine/revalidate/unlink journal;
- remote-history behavior after deliberate local byte collection; and
- exact status and recovery semantics for quota pressure and ENOSPC.

No object is unlinked in rev0973. `reclaimable_authority:false` remains true.
Diagnostic corruption quarantine remains separate from user version retention.

## Validation

Exact rev0973 source passed the fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 433 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 140 local-control, 87/87 observer, and 6/6 observer-race checks. The upgraded SQLite-owner source audit passed 43/43 checks, and the complete structural authority audit passed 292/292 checks. A clean Clang 17 Debug product dependency graph completed 239/239 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 320-check SQLite-owner suite in 2.89 seconds at 556,172 KiB peak RSS, the 433-check folder-owner suite in 26.11 seconds at 1,432,996 KiB peak RSS, and the 140-check local-control suite in 0.56 seconds at 94,148 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0972 parent SHA-256 matched 5d8c791ded176f4b76e685103bf75b7697d5e466f5f8236ef7bf822f03523ded and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 21/21 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,229,745 bytes with SHA-256 576051d058ff39a23b32d3aef2487e296a18a398a67e4e28bc5a331e4e8b043e. The registry-driven audit correction also added direct exact v5-to-v6 migration, restart, and malformed-cutpoint rollback proof.

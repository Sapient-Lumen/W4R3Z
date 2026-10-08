# AnonSync rev0878 revision notes

## Purpose

Rev0878 combines rev0877's live authenticated-channel capability with a narrow
effect-terminal immutable-file delivery path, then closes a newly identified
cross-owner projection race. It also hardens preclaim payload policy and repairs
package-proof coverage found by the complete registry.

## Primary parent and merge source

The primary lineage parent is the user-provided
`AnonSync-rev0877-2026.07.22.06.13-livechannelauthority-sslownership-streampoison-wirepreflight.zip`.

A separately validated cloudtainer branch based on rev0876 contained an
independent effect-terminal file-delivery implementation. Rev0878 merges that
implementation into the primary rev0877 channel-authority line, then adapts and
extends it. The evidence lineage records both archives; only the primary parent
defines the linked revision chain.

## Production C++ changes

### Live authority reaches filesystem settlement

`SyncReplicaFileDeliveryService` now accepts
`SyncReplicaDeliveryChannelAuthority` on claim, receive, and receipt application.
It validates the private capability before context access or durable work, passes
the same capability into the nested evidence service, and revalidates after the
arbitrary sender payload callback. The class is an explicit friend of the
move-only capability; no public mint or validation API was added.

The deterministic test capability remains linked only into the file-service test
executable.

### Payload size is checked before lease mutation

The causal owner claim core now accepts an optional exact operation kind and
maximum File payload size in addition to the complete wire model. The selected
canonical operation is restored, validated, and compared to the payload ceiling
before lease publication. Oversized work cannot increment attempts, mint a claim
ID, assign a worker, or alter the cutpoint.

This is an additive API change. Existing claim callers remain source-compatible.

### Scope-bound causal projection guard

`SyncReplicaSqliteProjectionGuard` is noncopyable and nonmovable. It owns a live
`BEGIN IMMEDIATE` transaction plus the exact fully restored snapshot. The owner
mints it only when:

- expected generation and cutpoint are syntactically valid;
- the current complete cutpoint exactly matches the transaction-bound evidence
  receipt;
- exact canonical operation evidence remains retained;
- the operation is a File in Active evidence state;
- it is the sole visible primary for its canonical path; and
- no preserved file alternate remains.

A mismatch commits an unchanged transaction and returns no guard. A successful
guard blocks competing causal writers until explicit commit or destructor
rollback.

### Effect materialization is cutpoint-bound

The receiver stages exact payload bytes, performs nested evidence admission, and
uses that receipt's generation and digest to request the projection guard. It
holds the guard through effect materialization, effect-database snapshot,
canonical receipt encoding, and receipt digest construction. The guard commits
only after those terminal bytes exist.

This prevents another SQLite owner from superseding the operation between a
loose projection check and visible filesystem publication.

### Effect-terminal immutable File slice

The merged production modules add:

- structural file-effect identity;
- bounded canonical file request/receipt framing;
- a separate exact SQLite payload/effect owner;
- private immutable create-new publication;
- exact restart reconciliation across rename/fsync/database ambiguity; and
- sender settlement only for `Published` and `AlreadyPublished`.

The effect owner is explicitly documented as an O(history) correctness oracle.

## Tests

New or expanded runtime tests cover:

- moved-from channel authority before claim/stage mutation;
- oversized committed payload before claim mutation;
- arbitrary payload callback channel revalidation;
- file-only claim filtering in the presence of tombstones;
- exact payload size and digest verification;
- capacity-before-evidence ordering;
- active/pending/quarantined/conflict dispositions;
- immutable publication and exact duplicate reconciliation;
- three-owner restart after an ambiguous terminal response;
- exact lease expiry, fresh attempt identity, and stale receipt fencing;
- post-publication/pre-database-mark recovery;
- private mode, owner, single-link, symlink, and hard-link rejection; and
- an independent SQLite writer blocked by a live projection guard, then admitted
  after commit, with an old cutpoint remaining a durable no-op.

## Audit/refactor work

`tools/audit_sync_replica_file_delivery.py` adds 23 explicit lexical-hygiene
checks for live-capability flow, preclaim policy, staging order, exact projection
guard coverage, terminal settlement, negative runtime cases, and production/test
link separation.

`tools/audit_sync_replica_sqlite_owner.py` is version 7 with 41 checks, including
guard nontransferability, exact cutpoint/primary conditions, independent-writer
runtime evidence, and stale-cutpoint no-op behavior.

The complete CTest registry initially found one failed atomic-publication source
audit. Runtime behavior was correct; `tools/verify_release_package.py` omitted the
new restart-reconciliation test from its mandatory package inventory. Rev0878
adds the missing requirement and the full rev0878 file surface. The audit was not
relaxed.

A comment describing the retained `BEGIN IMMEDIATE` guard as a “read-only
transaction” was corrected to describe it as an unchanged writer-serializing
transaction. The guard does not claim cross-store atomicity.

## Boundary findings

The receive path's overlapping lock order is causal SQLite → effect SQLite →
filesystem. Current effect-owner methods do not call the causal owner, so there
is no inverse nested path. Future code must retain one global order.

The guard intentionally holds a causal writer slot through O(history) effect
restore and file/directory synchronization. This is conservative correctness
oracle behavior, not production throughput architecture.

The next severe filesystem gap is stable root identity. The effect owner persists
normalized root-path text; it does not retain or attest one root directory object
across calls or restart.

The sender payload callback still executes after claim. Payload absence,
exception, or digest mismatch leaves a valid lease to expire or be classified by
future retry policy. Rev0878 prevents declaratively impossible size/wire claims,
not all local payload-availability churn.

## Compatibility and schema

The causal SQLite schema remains version 5. The projection guard adds no durable
row or migration. Claim API parameters are additive defaults.

The file-effect database remains its new exact schema version 1. It is not a
migration of the older shipped product database and is not used by
`anonsync_core`.

The file-delivery protocol is version 1 and supports File operations only.

## Deliberate nonclaims

Rev0878 does not claim a shipped service, ordinary replacement/update semantics,
tombstone effects, stable root identity, signed offline receipts, fair staging
retention, complete retry/dead-letter policy, complete membership/key lifecycle,
nonblocking transport, production-scale indexed ownership, anti-entropy,
compaction, anonymity, externally trusted provenance, or formal proof.

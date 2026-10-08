# AnonSync rev0869: SQLite replica cutpoint audit

## Executive diagnosis

The heart of AnonSync is **authority-preserving convergence**. Exact canonical
operations and their immediate causal edges are the durable facts. Active,
visible, pending, quarantined, head, counter, resource, and retry state are
interpretations or ownership records derived from those facts. The system is
correct only when a crash, duplicate, schema mutation, capacity decision,
summary mismatch, or optimization cannot promote a derived value into stronger
authority than the exact evidence permits.

Before rev0869 the reference model could explain what should happen, but the
persistence boundary could not yet prove that the required facts crossed one
commit together. That gap was mission-critical. An implementation could reserve
a local counter without retaining its operation, project a visible winner
without its exact evidence, enqueue bytes without the operation identity they
belonged to, forget a valid blocked operation at restart, or accept a locally
edited summary as history. Any of those failures converts a deterministic model
into a recovery-dependent protocol.

Rev0869 builds a deliberately narrow vertical slice: one SQLite database, one
folder, one local actor epoch, exact canonical evidence, exact projection,
exact local mint mapping, persisted policy, and sender outbox intents. The slice
is not the final product path. Its purpose is to establish the transaction and
restore invariants that later incremental and distributed work must preserve.

## Mission invariant

For one folder and trust/policy epoch:

> Equivalent exact canonical evidence and equivalent trust state must produce
> equivalent evidence classification, heads, and visible state. A local mint is
> authoritative only when its exact counter mapping and operation are committed
> together. A sender intent is retired only by exact settlement. A capacity
> block changes neither validity nor retained evidence. Every redundant row is
> rebuildable and must be rejected when it disagrees with exact evidence.

This has four independent verdict dimensions that a future wire protocol must
keep separate:

1. canonical envelope validity;
2. authenticated actor/membership admission;
3. graph applicability and deterministic projection; and
4. local retention availability.

Rev0869 persists the first, third, and fourth dimensions for the unauthenticated
reference operation format. The second remains missing.

## Durable authority map

The owner uses eight exact schema objects in `main`:

| Object | Authority |
|---|---|
| `sync_replica_meta` | folder/local actor identity, local counter, state and policy generations, persisted limits, exact counters, digests, structural cutpoint seal |
| `sync_replica_operations` | one canonical byte owner per operation ID plus remeasurable summaries and persisted evidence state |
| `sync_replica_parent_edges` | exact ordered immediate predecessor IDs for each retained child |
| `sync_replica_local_operations` | exact local counter to operation-ID authority mapping |
| `sync_replica_heads` | redundant deterministic causal-head projection |
| `sync_replica_visible` | redundant deterministic path-visible projection |
| `sync_replica_outbox` | lightweight unsettled destination/operation/generation intents |
| `sync_replica_outbox_operation` | acceleration index over operation and destination |

Every table is STRICT, but STRICT is treated only as storage-type hardening.
Semantic authority still comes from bounded exact decode, identity recomputation,
folder and actor checks, charge remeasurement, model restore, and row-for-row
projection comparison.

Unsigned 64-bit values are stored as exactly eight big-endian BLOB bytes. This
avoids silently narrowing the model's unsigned authority into SQLite's signed
integer range and makes byte length part of the schema contract.

## Exact schema as protocol evidence

The literal SQL stored in `main.sqlite_schema` is attested. The owner does not
silently migrate, repair, or tolerate extra protocol objects. That strictness is
intentional in a correctness oracle: an unreviewed trigger, view, or index can
change execution semantics even when table columns appear intact.

The first implementation scanned only names matching `sync_replica_*`. Audit
showed that was insufficient. SQLite stores the attached table separately as
`tbl_name`; a trigger called `unrelated_name` could still execute on
`sync_replica_outbox`. The final scan selects objects where either `name` or
`tbl_name` matches the namespace. It also stops after the exact contract plus
one witness and bounds aggregate schema SQL bytes, preventing an attacker from
turning attestation itself into unbounded work.

All owner SQL qualifies tables with `main.*`. This prevents TEMP tables or views
with the same names from shadowing reads and writes. It does not make TEMP
triggers irrelevant: a connection-local TEMP trigger can target `main` and
execute on that connection. That led to the next correction.

## Why precommit re-attestation is required

A normal sequence of “attest old state, write rows, commit” proves only that the
transaction began from a valid cutpoint. It does not prove that the exact rows
about to commit are the rows the owner intended to stage. A TEMP AFTER trigger
can mutate metadata or projection during a successful statement while remaining
outside `main.sqlite_schema`.

Every mutating path therefore follows this shape:

1. `BEGIN IMMEDIATE` through the typed transaction owner;
2. prove exact write authority for the database handle and transaction;
3. load and independently attest the complete old cutpoint;
4. run the pure model transition and construct intended outbox/policy state;
5. stage canonical rows, parent rows, local mapping, projection, outbox, and
   metadata;
6. reload the complete database while still in the same transaction;
7. re-decode exact operations, restore the model, rederive all projections and
   digests, and compare the staged cutpoint with the intended in-memory state;
8. commit only after exact equality.

The runtime test installs a TEMP trigger that silently changes staged metadata.
The staged reload observes the mismatch, throws, and lets the transaction owner
roll back. A caller never receives a successful operation for a cutpoint that
was not independently re-attested.

This is expensive, but it converts a subtle executable-schema ambiguity into a
clear correctness boundary. A later production owner may replace the global
reload with narrower proofs only after differential evidence shows the narrower
proof is equivalent.

## Canonical evidence restore

A load does not trust operation IDs, sizes, counts, or evidence-state labels in
isolation. For every operation row it:

- bounds and reads canonical bytes;
- decodes the exact operation under persisted limits;
- re-encodes/re-hashes through the canonical codec and verifies the ID;
- remeasures canonical bytes, context entries, and predecessor count;
- compares ordered parent rows with the operation's exact predecessor IDs; and
- restores the complete pure `SyncReplicaModel` from the durable evidence set.

It then compares model-derived evidence states, heads, visible rows, retained
resource totals, active/evidence counts, local actor compromise state, and all
digests with the stored rows and metadata. `PRAGMA foreign_key_check` is an
additional structural check, not a replacement for semantic restore.

Foreign-key enforcement is enabled and read back before schema creation or any
transaction. This ordering matters because SQLite documents that changing the
foreign-key pragma inside a transaction has no effect.

## Local mint authority

A local operation has two linked identities: its canonical operation ID and the
local actor's monotonically increasing counter. The evidence set alone is not
sufficient to reconstruct which same-dot operation was the locally minted one
if a fork exists. Rev0869 therefore persists `counter_be -> operation_id` rows
and hashes the exact ordered map in a domain-separated `local_operation_digest`.
The cutpoint digest includes that map digest alongside operation, evidence,
visible, and outbox digests.

Local file/tombstone publication validates and deduplicates destination IDs,
rejects the local device as a destination, computes exact outbox count and
destination-byte growth, and proves both outbox ceilings before asking the model
to mint. A rejected fanout cannot burn a local counter. The operation, local
mapping, projection, metadata, and all intents then publish in one transaction.

Two concurrent owners on separate handles are tested against the same file.
`BEGIN IMMEDIATE` serializes writers; both completed operations receive distinct
contiguous local counters and restore to one exact attested mapping.

## Capacity remains separate from validity

The persisted model and outbox policies are independent. For remote admission,
canonical/folder validation and exact duplicate handling remain model
responsibilities. A `Duplicate` or `CapacityBlocked` result commits an empty
transaction and returns without advancing state generation or rewriting
projection rows. The policy that caused a block is stored in metadata, so a
restart cannot silently reinterpret the same database under new caller
defaults.

Policy changes are explicit transactions. A replacement first restores all
retained operations under the proposed model limits and proves current outbox
count/destination bytes fit. Only then are policy and state generations
advanced. The test demonstrates that the same exact remote operation remains
blocked after restart and becomes admissible only after an explicit larger
policy is committed.

## Outbox ownership and work reduction

A naive durable fanout model copies the full operation once per destination.
That multiplies canonical bytes, validation, storage, and tamper surfaces by
fanout. Rev0869 stores canonical bytes once and creates lightweight
`destination_device_id + operation_id + enqueued_generation` rows.

The design is analogous to an unsettled delivery owner: sender state remains
until an exact destination/operation acknowledgement retires it. ACK deletion
changes only that one intent. It cannot erase canonical evidence or another
destination's intent. Missing ACK is idempotent and does not advance generation.

`outbox_delivery_or_throw` still performs the full O(history) attested restore,
which is intentionally conservative. It no longer calls the public snapshot API
and then copies the complete durable publication again; only the requested
operation is copied out. The next refactor should introduce a point-read path
whose narrow proof is checked against the global restore oracle.

## Crash frontier

The most important crash cutpoint is after the sender intent has been staged but
before commit. If evidence or local counter were durable without outbox, the
operation could be permanently unsent. If outbox were durable without evidence,
the sender could advertise an operation it cannot reproduce.

The final probe launches a pinned copy of the current executable using the
project's test-only self-exec owner. The child verifies the exact executable,
process group, environment, signal defaults, and descriptor hygiene before
parsing its instruction or opening SQLite. An SQLite update hook exits with
status 73 after an outbox insert. The parent reopens and attests the database;
it observes the old state generation and none of the staged evidence,
projection, local mapping, or outbox rows.

The first version used raw `fork()`, which the complete source audit rejected.
That failure was valuable: a crash oracle that executes complex C++ and SQLite
in a post-fork child can inherit locks and state that make the result ambiguous.
The test now uses the same fresh-image boundary as seven other crash/fault
campaigns, and all dependent inventory audits were updated rather than waived.

## Structural seal and its limit

The cutpoint digest frames folder identity, local actor and epoch, policy and
state generations, exact semantic resource counters, compromise state, and the
local-operation, operation-set, evidence-set, visible-state, and outbox digests.
It catches torn or casual edits where one summary is changed without all related
facts.

It is deliberately labeled an **unkeyed structural seal**. A local attacker that
can rewrite the entire database can recompute it. The seal is not an actor
signature, hardware-backed monotonic counter, filesystem integrity guarantee,
or authenticated backup. The next security layer must decide who is trusted to
sign or MAC local cutpoints, how keys rotate, how rollback is detected, and how
recovery works without granting stale state new authority.

## Severe or wasteful patterns found

### Corrected now

- name-only schema inventories that missed execution attachments;
- attestation only before staging, with no proof of the commit candidate;
- broad set digests that omitted exact local mint mapping;
- raw post-fork application execution in a crash test;
- per-destination canonical operation copies;
- outbox pressure discovered after local counter mint;
- restart-time policy defaults that could reinterpret a durable database; and
- delivery through a second public full-snapshot copy.

### Still intentionally expensive

- every public read/mutation is O(history);
- every mutation globally reprojects and rewrites heads/visible rows;
- outbox lookup loads the whole evidence set;
- exact schema SQL is compared as a monolith rather than versioned through an
  authenticated migration protocol;
- no physical page/WAL/disk charge is included in semantic limits; and
- no workload admission deadline bounds total restore CPU or I/O.

These costs are acceptable for a reference authority only. They become denial-
of-service surfaces if exposed directly to arbitrary peers or large histories.

## Online research synthesis

Official SQLite transaction documentation confirms that reads and writes occur
inside transactions and that only one write transaction exists at a time. That
supports using one SQLite write transaction as the publication cutpoint, while
not proving filesystem durability by itself.

SQLite documents that foreign keys are disabled by default per connection and
cannot be enabled in the middle of a transaction. The owner explicitly enables
and verifies them before use. STRICT tables constrain stored types but do not
validate canonical operation semantics, so exact decode and reprojection remain
mandatory.

SQLite's trigger documentation makes TEMP triggers on non-TEMP tables an
explicit connection-local execution surface and recommends schema qualification
of the target. That directly motivates `main.*` qualification and staged
re-attestation. The schema audit's use of `tbl_name` is an implementation
inference from SQLite's schema representation: executable attachment authority
must be inventoried by target as well as object name.

WAL documentation distinguishes atomic commit from power-loss durability and
notes that synchronous mode, checkpointing, WAL companions, and multi-database
transactions matter. Rev0869 therefore keeps the cutpoint in one `main`
database and makes no VFS/fsync/power-loss durability claim beyond SQLite's
configured behavior. The bundled SQLite 3.53.3 is newer than the documented
3.51.3 WAL-reset correction, but that does not eliminate hardware, VFS,
operator-copy, or application misuse risks.

AMQP 1.0 describes unsettled delivery state and sender forgetting only on
settlement. AnonSync uses that as a conceptual analogy: an outbox intent remains
owned until exact acknowledgement. It does not implement AMQP framing,
transactional resources, or its delivery guarantees.

Primary-source URLs and access dates are in
`REVISION_EVIDENCE/rev0869/RESEARCH.md`.

## Speculative architecture after this cutpoint

A staged path that preserves the mission:

1. **Authenticated operation envelope.** Bind canonical content to actor key,
   membership epoch, folder epoch, and algorithm suite. Define rotation,
   revocation, recovery, and old-epoch treatment before accepting arbitrary
   peers.
2. **Point-read sender leases.** Add bounded lease/in-flight state, retry count,
   backoff, wake generation, and exact settlement. Differentially check every
   point-read result against the current global restore.
3. **Incremental projector.** Recompute only the affected dependency/path
   subgraph, but retain the global oracle in tests and periodic audit. Publish
   incremental index changes in the same evidence transaction.
4. **Two-process protocol slice.** Use authenticated head/dependency exchange,
   exact-ID requests, bounded response bytes, and crash probes at sender commit,
   transfer, receiver commit, ACK, and sender retirement.
5. **Payload binding.** Verify chunks and final file publication against the
   operation's exact payload commitment before changing filesystem-visible
   state.
6. **Retention lifecycle.** Add causal-stability/checkpoint evidence,
   compaction, tombstone policy, old-replica rejoin, and reserved recovery
   capacity. Never equate age with safe deletion.
7. **Physical resource governance.** Measure SQLite pages, WAL, snapshots,
   filesystem blocks, RSS, allocator overhead, CPU, and wall time in addition
   to stable semantic charge.
8. **Privacy model.** Analyze membership leakage, dependency graph shape,
   pressure responses, retry timing, path metadata, padding, cover traffic,
   session unlinkability, and compromise recovery before using the name
   “anonymous” as a security claim.

## Remaining high-risk gaps

- no authenticated actor or membership provenance;
- no keyed local-store seal or rollback-resistant monotonic authority;
- no production integration of this owner;
- no authenticated transport or anti-entropy protocol;
- no retry lease/backoff/wake state;
- no payload/chunk materialization;
- no causal stability, compaction, tombstone GC, or old-replica rejoin rule;
- no per-principal fairness or Sybil resistance;
- no hard global CPU/I/O deadline for restore;
- no actual SQLite/WAL/disk/RSS bound;
- no incremental projector; and
- no anonymity or metadata-hiding threat model.

## Bottom line

Rev0869 closes the most important local gap between the replica oracle and a
real durable transaction. It also demonstrates why “atomic SQLite write” is not
sufficient wording: schema execution surfaces, exact local authority mapping,
staged-state re-attestation, persisted policy, and process-correct crash tests
all matter. The next work should optimize and distribute this cutpoint without
splitting or weakening its authority.

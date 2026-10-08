# Revision notes: AnonSync rev0869

## Mission increment

Rev0869 carries the replica semantics built in rev0865–rev0868 across the first
real SQLite transaction boundary. The new `SyncReplicaSqliteOwner` owns one
folder and one local actor epoch. It binds exact canonical operation evidence,
immediate parent edges, local counter authority, deterministic evidence and
visible projection, persisted limits, exact semantic resource counters, and
sender outbox intent into one durable cutpoint.

The owner intentionally reuses the pure `SyncReplicaModel` as an executable
oracle. SQLite rows are not accepted merely because constraints and stored
summaries look plausible: every load decodes exact canonical bytes, recomputes
operation identity and charge, restores the model, rederives heads and visible
state, checks every redundant row, and verifies domain-separated digests.

## Principal C++ changes

1. Added `src/sync_replica_sqlite_owner.hpp/.cpp`, a noncopyable and nonmovable
   owner over one exact `SyncSqliteDbHandleSlot`.
2. Added separate persisted evidence limits and outbox count/destination-byte
   limits. Sender pressure is not represented as operation invalidity.
3. Added an exact eight-object `main.sqlite_schema` contract: metadata,
   operations, parent edges, local operations, heads, visible rows, outbox, and
   the outbox lookup index. Every table is STRICT.
4. Added bounded schema attestation over both object name and attachment target.
   Extra, missing, changed, or reattached protocol objects fail closed.
5. Added explicit connection hardening and verification:
   `foreign_keys=ON`, `trusted_schema=OFF`, exact schema SQL, and
   `foreign_key_check` on every cutpoint load.
6. Encoded all durable unsigned 64-bit authorities as exact eight-byte
   big-endian BLOBs, avoiding SQLite signed-integer range truncation or
   affinity-based reinterpretation.
7. Added exact canonical operation decode/hash/size/context/predecessor
   remeasurement and exact parent-edge comparison.
8. Added complete model restore and row-for-row attestation of evidence state,
   heads, visible rows, local counter mapping, outbox, resource counters,
   policy, identity, and generations.
9. Added a domain-separated `local_operation_digest` over folder, actor epoch,
   and the exact counter-ordered local operation IDs. It is bound into the
   structural cutpoint digest.
10. Added local file and tombstone mint paths that check destination identity,
    duplicate/self fanout, and independent outbox ceilings before reserving the
    next counter. Evidence, projection, local mapping, and all outbox intents
    then commit together.
11. Added remote admission with durable `Duplicate` and `CapacityBlocked`
    no-ops. Only newly retained evidence advances the state generation.
12. Added exact per-destination ACK retirement and outbox delivery that returns
    the requested operation without constructing a second public full snapshot.
13. Added explicit durable policy replacement. The owner restores retained
    evidence under the replacement model limits and checks current outbox fit
    before incrementing policy and state generations.
14. Added `SyncReplicaModelLimits::operator==` and a noncopying const view of
    local operation IDs so durable attestation does not clone all local
    authority solely to hash it.

## Transaction and crash discipline

Every mutating operation begins an IMMEDIATE typed transaction, proves its write
authority, loads and attests the complete old cutpoint, applies the pure model,
stages exact SQL changes, updates metadata, then reloads and re-attests the
complete staged cutpoint before COMMIT. This second restore is important: a
connection-local TEMP trigger can mutate protocol rows despite a clean
`main.sqlite_schema` contract. A mismatch raises and the typed transaction
rolls back.

The crash probe enters the established pinned self-exec process owner. The child
verifies image, process group, environment, and descriptor hygiene before
opening SQLite. An update hook exits with reviewed status 73 immediately after
the outbox insert and before commit. Reopening the database yields the old
attested generation with no partial evidence, local counter, projection, or
outbox state.

## Audit and refactor findings

The implementation audit corrected four cross-cutting problems while they were
still local:

- a main trigger with an unrelated name could attach to a replica table and
  evade a name-only schema scan;
- an attestation performed only before staging could miss silent TEMP-trigger
  mutation before commit;
- broad operation/evidence digests did not bind the exact local
  counter-to-operation map under same-dot substitution; and
- the first crash test bypassed the project's centralized process boundary with
  raw `fork()`.

The final design scans `name OR tbl_name`, re-attests staged state, binds a
separate local map digest, and uses the audited self-exec owner. The dependent
raw-fork, self-exec, and allocator source audits now describe eight fresh-image
campaigns and 32 inherited-or-fresh process sites exactly.

The outbox was also refactored to remove per-destination operation copies. One
canonical operation row can back many lightweight intents. Delivery still has
O(history) restore cost, but it copies out only the requested operation rather
than constructing a second full publication snapshot.

## Tests and audits

Added `tests/sync_replica_sqlite_owner_test.cpp` with 56 checks for:

- atomic local publication and one canonical row across multiple destinations;
- restart-stable snapshots, policy, generations, and outbox;
- TEMP table/view shadow resistance through explicit `main.*` names;
- exact ACK retirement and idempotence;
- durable capacity block followed by explicit policy expansion and retry;
- same-dot fork projection and tamper detection;
- SQL-stage rollback from outbox and metadata triggers;
- schema drop, metadata tamper, outbox tamper, and unrelated-name trigger
  attachment rejection;
- precommit detection and rollback of silent TEMP-trigger row mutation;
- exact local counter-map digest substitution detection;
- pending-child restart and late-parent activation;
- duplicate, self-destination, and outbox pressure rejection before mint;
- two concurrent writers serializing local counter authority; and
- real process death after outbox insertion but before commit.

Added `tools/audit_sync_replica_sqlite_owner.py` with 28 fail-closed structural
checks. Updated the raw-fork, self-exec, allocator, and package-verifier audits
to include the new owner and its crash campaign.

## Validation

Final source results:

- GCC Debug all-target build followed by a zero-work Ninja rebuild;
- 172/172 registered tests: 171/171 parallel and one isolated serial owner;
- 52/52 registered audits;
- 2,144/2,144 focused runtime checks under GCC across six executables;
- the same six executables under Clang 17 Release with `-Werror`;
- the same six under GCC ASan/UBSan with leak detection and halt-on-error;
- 20/20 repeated final-source owner stress iterations;
- Clang default interprocedural static analysis over three pure replica
  translation units with zero diagnostics;
- bounded Clang shallow analysis of the SQLite owner and its test with zero
  diagnostics. Default interprocedural analysis of the 1,955-line owner exceeded
  the execution window and is explicitly not claimed as a pass;
- owner source audit 28/28, raw-fork inventory 11/11, self-exec audit 36/36,
  and allocator-fault audit 101/101; and
- exact rev0868 parent ZIP and directory verification, source-patch replay,
  active projection, manifest, and final package verification.

## Scope and remaining work

The owner is O(history) and rewrites full projection tables. It is not yet wired
into the integrated product path. The structural seal is unkeyed. No real
remote authentication, membership/key epoch protocol, retry lease, backoff,
wake condition, payload/chunk publication, causal stability, compaction,
tombstone GC, physical disk/WAL/RSS limit, authenticated local-store seal,
privacy model, or two-process sender/receiver convergence path is claimed.

The highest-leverage next step is to split correctness authority from
incremental acceleration without weakening restore: add an authenticated actor
and membership envelope, point-read outbox leasing/settlement, an incremental
affected-subgraph projector checked against this global oracle, and a real
sender/receiver crash-retry test. Keep one database cutpoint until there is an
explicit cross-store commit protocol.

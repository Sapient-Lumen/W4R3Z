# Durable TLS membership authority audit — rev0891

## Mission connection

AnonSync is not allowed to derive application authority from a convenient
configuration object merely because that object is immutable in memory. The
project's governing rule is stricter:

> Exact authorized history owns identity and every later capability; a summary
> or label may accelerate a decision, but may not manufacture the cutpoint that
> decision claims to represent.

Rev0890 correctly removed arbitrary application code from the live
post-handshake membership frontier. It introduced a canonical immutable mapping
from exact peer SPKI digests to AnonSync actors for one folder and one local
actor. What it did not own was the history that selected that mapping. Any
caller could construct a valid snapshot with any positive `policy_epoch`, and
the accepted server had no evidence that the value had been durably published,
that it extended the last trusted policy, or that the database had not been
replaced by an older internally valid copy.

Rev0891 implements the first durable membership-history owner. The narrow claim
is:

> One accepted-session membership capability is emitted only from a complete,
> canonically reconstructed SQLite cutpoint after an exact compare-and-swap
> publication has committed.

This does not yet implement signed enrollment or an external anchor store. It
turns the rev0890 snapshot from freely constructible configuration into a value
that can cross the accepted-session boundary only through durable owner
issuance.

## Authority decomposition

The revision deliberately separates three values that are easy to conflate:

1. `SyncReplicaTlsMembershipSnapshot` is the canonical immutable policy value.
   It binds folder, local actor, policy epoch, sorted SPKI-to-actor entries,
   entry count, and snapshot digest.
2. `SyncReplicaTlsMembershipAnchor` is a retainable observation of one append-
   only history cutpoint: exact state generation plus exact chain digest.
3. `SyncReplicaTlsMembershipAuthority` is a move-only in-process capability
   constructible only by `SyncReplicaTlsMembershipSqliteOwner` after a committed
   policy exists and complete reconstruction succeeds.

The accepted TLS server consumes the third value by value. A caller can still
construct snapshots for planning and validation, but cannot pass a raw snapshot
across the server's durable membership frontier.

The move-only wrapper prevents one issued wrapper from being copied into
multiple calls. It is not a one-session-per-generation nonce. The owner may
remint multiple wrappers for the same committed cutpoint. Nor is it live
revocation: a capability issued before a later rotation remains the selected
policy for the already-started accept/handshake call. The issuance point is the
explicit policy cutpoint.

## Persistent schema

The owner uses three exact `STRICT` tables:

- `sync_replica_tls_membership_meta` stores one service identity and the current
  committed cutpoint;
- `sync_replica_tls_membership_updates` stores one append-only chain record per
  state generation; and
- `sync_replica_tls_membership_entries` stores the complete canonical snapshot
  entries for every retained generation.

The metadata row binds:

- schema version;
- folder ID;
- local device ID and actor epoch;
- current state generation;
- current policy epoch;
- current entry count;
- current snapshot digest; and
- current chain digest.

Every update row binds:

- contiguous positive state generation;
- strictly increasing positive policy epoch;
- exact entry count;
- previous chain digest;
- canonical snapshot digest; and
- derived current chain digest.

Every entry row is keyed by generation and exact lowercase SHA-256 SPKI. Actor
identities are reconstructed through the same canonical snapshot constructor
used for new policy candidates.

The entries table deliberately retains complete historical snapshots. That is
expensive, but it makes this owner a transparent correctness oracle: every read
can regenerate every snapshot digest and every chain link without trusting a
current-state cache.

## Canonical chain

The deterministic empty-history anchor uses the domain:

```text
anonsync:sync-replica-tls-membership-chain:genesis:v1
```

It binds schema version, folder ID, and local actor.

Each update uses the domain:

```text
anonsync:sync-replica-tls-membership-chain:update:v1
```

and binds, in order:

1. schema version;
2. folder ID;
3. local actor;
4. state generation;
5. policy epoch;
6. entry count;
7. previous chain digest; and
8. canonical snapshot digest.

Variable-length fields are length framed and integers are encoded as unsigned
big-endian 64-bit values. The chain therefore closes accidental concatenation,
architecture, ordering, service-identity, sequence, and snapshot substitution
ambiguities.

The chain is unkeyed. It detects ordinary corruption and supports comparison to
a separately retained trusted anchor. It is not a signature, author identity,
quorum decision, key epoch, freshness statement, or defense against a malicious
writer that can replace both database and anchor.

## Exact publication state machine

`publish_or_throw` performs this order:

1. validate the expected current anchor and positive persistable policy epoch;
2. construct and canonicalize the complete candidate snapshot before acquiring
   SQLite writer authority;
3. reject peer actor epochs that cannot fit SQLite's signed integer range;
4. enter `BEGIN IMMEDIATE`;
5. re-attest the connection and durable backend profile;
6. re-attest the exact schema;
7. reconstruct and validate complete metadata, history, entries, snapshots, and
   chain links at that write cutpoint;
8. compare the observed current anchor to the caller's expected anchor;
9. require the policy epoch to advance strictly;
10. require the candidate append to fit both retained-history ceilings;
11. derive the next chain digest;
12. append the update row;
13. append the complete canonical entry set;
14. advance the one metadata row;
15. allocate the caller-visible immutable authority state;
16. commit; and
17. return the move-only capability.

Step 15 is intentionally before `COMMIT`. The initial implementation allocated
the return state after commit. A local allocation failure at that point would
have advanced durable policy but thrown before returning the requested
capability. The corrected order makes allocation failure roll the transaction
back. A later SQLite commit error can still have storage-system-specific
ambiguity; rev0891 does not claim to eliminate the general uncertainty of a
failed durable commit.

No caller callback, network operation, filesystem lookup, or external anchor
write runs inside the append transaction.

## Compare-and-swap and first-open serialization

Publication compares one exact `(generation, chain_digest)` anchor under the
same `BEGIN IMMEDIATE` transaction that appends the new policy. A stale owner on
a second SQLite connection cannot overwrite a newer committed generation.

Schema initialization follows the same discipline. The durable backend profile,
existing-schema observation, empty-database decision, table creation, metadata
insertion, exact schema attestation, and commit are serialized under
`BEGIN IMMEDIATE`. Two independent connections racing on first open therefore
cannot both act on an authority-free observation made before writer ownership.

SQLite documents that only one write transaction can exist at a time and that
`BEGIN IMMEDIATE` starts the write transaction immediately, failing with
`SQLITE_BUSY` if another writer is active. This is the local serialization
primitive; it does not create a transaction with an external anchor store.

## Read and restart reconstruction

Every `snapshot_or_throw` uses one deferred transaction and validates:

- exact connection profile and durable journal profile;
- exact main and TEMP schema closure;
- one metadata row and exact service identity;
- bounded history and retained-entry row counts;
- contiguous generations beginning at one;
- strictly increasing policy epochs;
- lowercase fixed-size digests;
- exact previous-chain continuity;
- canonical entry rows for each generation;
- recomputed snapshot digest;
- recomputed chain digest;
- absence of orphan entries;
- exact correspondence between metadata and the final history row; and
- optional trusted-anchor continuity.

Only after reconstruction succeeds does the owner remint current authority.
Restart therefore derives capability from durable evidence rather than cached
process belief.

The implementation is intentionally O(history + retained entries) per read and
mutation. It is appropriate as a migration, recovery, differential-testing, and
correctness oracle. It is not the desired high-throughput production reader.

## External anchor semantics

A caller may retain an anchor outside the membership database and supply it to a
later read. The owner rejects when:

- the trusted generation is newer than the database, proving whole-database
  rollback below retained state; or
- the database's chain digest at that exact generation differs, proving a fork
  through the retained point.

An older trusted anchor is accepted when the database is a valid extension
through that point. That is useful during atomic-anchor update design: a valid
newer database need not be rejected merely because an independently persisted
anchor update lagged.

This also defines the remaining gap precisely. Rev0891 provides the anchor
format and verification rule, but no external store. Updating database and
anchor is not atomic in this revision. A production design needs a separate
monotonic or authenticated store with explicit crash ordering and recovery.
The Update Framework is a useful conceptual comparison: its client workflow
retains trusted versions in non-volatile storage, rejects rollback, and requires
exact sequential root updates. Rev0891 borrows the separation between current
metadata and separately retained trust state, not TUF's signature or delegation
claims.

## Schema closure audit

Exact table SQL alone was insufficient. SQLite permits schema objects with names
unrelated to their target tables, and permits connection-local TEMP triggers on
non-TEMP tables. A prefix-only inventory would therefore miss an index or
trigger named, for example, `unowned_index` but attached to a membership table.

The owner closes both dimensions:

- in `main.sqlite_schema`, every SQL-bearing object whose name has the membership
  prefix **or whose `tbl_name` names an owned table** is counted, and exactly the
  three reviewed tables must remain;
- in `temp.sqlite_schema`, any prefixed object or object attached to an owned
  table is rejected.

Compiled tests add an arbitrary-named main index and a TEMP trigger attached to
an owned table. Both fail before authority reconstruction. This is especially
important because SQLite documents that a TEMP trigger can target a non-TEMP
main table and is visible only to the connection that created it.

Views that merely read authority tables do not alter owner statements and are
not included by `tbl_name` unless they use the reserved prefix. Confidentiality
against a same-process database user is not claimed.

## Dedicated connection profile

Schema closure is only one part of the SQLite authority boundary. The owner now
configures and re-attests a dedicated connection profile:

- defensive mode enabled;
- trusted schema disabled;
- schema triggers disabled;
- schema views disabled;
- extension loading disabled;
- double-quoted string compatibility disabled where supported;
- attach creation and attach writes disabled where supported;
- attached-database limit set to zero;
- trigger-depth limit set to zero;
- `trusted_schema=OFF`;
- `query_only=OFF`;
- `read_uncommitted=OFF`;
- `ignore_check_constraints=OFF`; and
- no database names other than `main` and optional `temp` present.

Each snapshot and publication rechecks the profile inside its transaction. A
caller that later reenables a mutable facility cannot continue using an old
owner as though the connection were unchanged.

This profile limits accidental schema execution, dirty-read authority, ignored
constraints, extension injection, and attached-schema ambiguity. It is not
same-process isolation. Code with arbitrary memory access or control over the
SQLite handle can still deny service or corrupt the process.

## Durable backend profile

The owner refuses:

- an in-memory database or handle with no nonempty main filename;
- a read-only main database;
- `MEMORY`, `OFF`, or another unreviewed journal mode;
- WAL below `synchronous=FULL`; and
- rollback-journal `DELETE`, `TRUNCATE`, or `PERSIST` below
  `synchronous=EXTRA`.

The WAL/rollback distinction is deliberate. Current SQLite documentation says
that WAL `FULL` synchronizes the WAL at every commit and is durable across power
loss, while WAL `NORMAL` can lose the latest transaction. For rollback journals,
`FULL` is not necessarily power-loss durable; `EXTRA` adds the directory sync
needed for the stronger durability claim.

These are necessary policy observations, not proof that the selected VFS,
filesystem, controller, virtualization layer, or physical device honors sync
requests. The filename check is also not stable path identity. Rev0891 does not
bind mount namespace, inode generation, directory capability, storage device,
or VFS implementation for the SQLite file.

## Retention ceilings and a corrected crossing-append defect

Complete history is bounded by:

- 65,536 history records; and
- 4,194,304 retained entry rows.

Each snapshot remains bounded by the existing 65,536-entry limit.

The first implementation checked these ceilings only during reconstruction. That
left a severe edge defect: an append could cross a ceiling, commit successfully,
and cause every later reconstruction to reject the now-over-limit database. The
corrected publication path carries the exact retained-row count out of complete
reconstruction and applies a checked predicate under `BEGIN IMMEDIATE` before
inserting anything.

The pure predicate is exposed for planning and exact boundary tests, but its
positive answer is not authority. The owner repeats it against the exact
transactional state. Compiled tests cover the final admissible history append,
first rejected history append, full retained-row state with an empty update,
first rejected retained row, already-overflowed input, and per-snapshot overflow.

The ceilings prevent unbounded restoration; they do not provide compaction.
Once history reaches the limit, a deliberate checkpoint/rekey/migration policy
is required before further nonempty or empty policy updates.

## Failure matrix

| Observation | Publication mutation | Capability | Required recovery |
|---|---:|---:|---|
| empty valid database | none | none | publish first policy |
| stale expected anchor | none | none | reread and reconcile |
| nonincreasing policy epoch | none | none | issue newer policy version |
| unpersistable actor epoch | none; rejected pre-writer | none | correct candidate |
| crossing retention ceiling | none | none | compact/migrate by explicit policy |
| connection profile changed | none | none | discard/reconfigure connection |
| attached schema present | none | none | use dedicated connection |
| schema object added | none | none | investigate/repair database |
| entry or chain tamper | none | none | restore from trusted evidence |
| trusted anchor newer than DB | none | none | treat as rollback/recovery event |
| trusted digest differs at generation | none | none | treat as fork/replacement event |
| allocation before commit fails | transaction rolls back | none | retry under resource policy |
| commit succeeds | complete new generation | move-only authority | retain/update external anchor |

## Compiled coverage

The owner test is composed into the real TLS transport executable and covers:

- two-connection concurrent first-open serialization;
- exact genesis and no authority before first publication;
- canonical input ordering and exact SPKI lookup;
- move-only authority behavior;
- strict profile installation and mutation detection;
- rejection of an attached database;
- WAL `NORMAL`, rollback `FULL`, synchronous `OFF`, memory journal, and in-memory
  database rejection;
- pre-writer rejection of a peer actor epoch outside SQLite integer range;
- exact retention-predicate boundaries;
- first publication and restart reconstruction;
- stale same-owner and stale second-connection compare-and-swap rejection;
- strict policy-epoch monotonicity;
- key rotation/revocation by complete snapshot replacement;
- acceptance of an older anchor on a valid extension;
- future-anchor rollback detection;
- digest-divergent anchor rejection;
- whole-database rollback detection using a separately retained newer anchor;
- wrong folder and local-actor rejection;
- entry-row, chain-row, orphan-row, main-schema, and TEMP-schema tamper rejection;
  and
- end-to-end TLS result attribution of generation, snapshot digest, previous
  chain digest, and current chain digest.

Lexical audits guard the reviewed shape and explicitly disclaim semantic proof.
Independent compilers, sanitizers, stress runs, complete CTest, and release
package verification provide separate evidence.

## Online primary sources

Sources accessed in the cloudtainer on 2026-07-23:

- SQLite PRAGMA documentation, especially `journal_mode` and the current
  `synchronous` durability matrix:
  https://sqlite.org/pragma.html
- SQLite WAL documentation, including one-writer semantics and WAL commit sync
  behavior:
  https://sqlite.org/wal.html
- SQLite transaction documentation, including read snapshots and
  `BEGIN IMMEDIATE`:
  https://sqlite.org/lang_transaction.html
- SQLite CREATE TRIGGER documentation, especially TEMP triggers on non-TEMP
  tables:
  https://sqlite.org/lang_createtrigger.html
- The Update Framework specification, for separately persisted trusted versions
  and rollback checks:
  https://theupdateframework.github.io/specification/latest/

## What remains missing

The highest-priority membership work after this revision is:

1. a separately owned, crash-consistent external anchor store;
2. authenticated or threshold-signed policy updates with signer/key-epoch
   evidence;
3. explicit enrollment, revocation, recovery, and overlap semantics;
4. a revocation-freshness rule for already issued or long-running accept calls;
5. signed reason/audit metadata and policy expiry/freeze handling;
6. an incremental current-state reader differentially tested against this full-
   history oracle;
7. explicit compaction/checkpoint authority before hard ceilings are reached;
8. stable storage-path/VFS/device evidence where deployment requires it; and
9. integration into the shipped executable as the sole membership source.

## Nonclaims

Rev0891 does not claim signed provenance, an external anchor store, atomicity
between SQLite and a second trust store, protection from a malicious local
writer, same-process isolation, live revocation of already-issued capabilities,
policy expiry, freeze-attack prevention, production-scale reads, compaction,
read-only serving, stable filesystem-path identity, storage-device durability,
a bounded listener pool, internet deployment safety, anonymity, unlinkability,
traffic-analysis resistance, formal verification, or externally trusted build
provenance.

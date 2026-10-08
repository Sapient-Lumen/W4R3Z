# File-effect device isolation and schema migration audit — rev0889

## Executive finding

The recovered rev0889 worktree contained a half-converted file-effect schema:
new device-limit fields existed in portions of the owner, while constructor
routing, restart attestation, migration, runtime coverage, and documentation
still described schema v2. That state was unsafe to seal. Depending on the exact
source snapshot, it could fail compilation, reject an existing database without
a migration path, or expose accounting fields without making admission policy
and the durable cutpoint agree.

Rev0889 completes one narrow correction:

- exact schema v3 persists per-`device_id` effect-count and retained-payload
  limits;
- every load derives actor-epoch and device usage from the complete retained
  effect closure;
- the derived device partition is bound by `device_count`, a dedicated
  `device_usage_digest`, and the schema-v3 cutpoint digest;
- unique admission applies folder limits first and device limits second;
- exact duplicates remain admissible even when a current policy is saturated;
- actor epoch rotation does not reset a device charge;
- an exact schema-v2 database is re-attested and migrated in one
  `BEGIN IMMEDIATE` transaction; and
- the file-delivery layer keeps the violated device boundary local while the
  wire retains the existing generic `EffectCapacityBlocked` receipt.

This is durable device isolation, not user fairness, storage reclamation, or a
membership proof.

## Authority model

### Canonical rows remain primary authority

The authoritative retained facts are still the exact effect rows: canonical
operation bytes, payload bytes, effect identity, staged/published state, and
transition generations. Actor and device usage are deterministic projections of
those rows. The owner reconstructs them on every load before trusting metadata.

Schema v3 persists only compact witnesses needed to detect drift cheaply and to
bind policy to the durable cutpoint:

- `device_count`;
- `device_usage_digest`;
- `max_effects_per_device`;
- `max_retained_payload_bytes_per_device`; and
- a v3 cutpoint digest covering the legacy policy, the two device limits,
  state totals, effect-set digest, and device-usage digest.

No cached usage counter authorizes admission independently. A future indexed
owner may persist counters, but it must remain differentially equivalent to this
full-history oracle.

### `device_id` is deliberately narrow

A device quota aggregates every retained actor epoch whose exact operation actor
has the same `device_id`. This closes the immediate epoch-rotation bypass.

It does not prove that `device_id` identifies a person, account, organization,
paid tenant, or current member. A party able to enroll arbitrary new device IDs
can still evade this boundary. Durable membership identity, membership-policy
epochs, enrollment limits, key rotation, revocation, and rejoin rules remain
above this owner and are not inferred here.

### Admission order is deterministic

For a validated new file operation the owner checks, in order:

1. receiver-local destination path capability;
2. exact operation/payload duplicate;
3. folder effect-count budget;
4. folder retained-payload-byte budget;
5. device effect-count budget; and
6. device retained-payload-byte budget.

The first violated constraint is returned in the local diagnostic. Folder caps
remain the final aggregate safety boundary; device caps isolate one existing
identity from consuming all remaining headroom. Duplicate reconciliation occurs
before quota enforcement because replaying an already-retained identity creates
no new resource charge and is required for crash/response-loss recovery.

An existing database may already exceed a newly introduced device cap. Those
rows remain canonical and are never deleted or rewritten by migration. The
saturated device is blocked only from additional unique admission; exact
retries still reconcile.

## Exact v2-to-v3 migration

The owner accepts only one of three database states:

- no schema, which creates exact v3;
- exact v3, which is fully restored and re-attested; or
- exact v2, which is eligible for the single supported migration.

Any extra, missing, renamed, or textually different schema object is refused.
For v2, the migration transaction:

1. validates the two incoming device-limit fields;
2. restores the exact persisted v2 folder/root identity and all legacy limits;
3. decodes and validates every retained operation and payload row;
4. recomputes and matches the v2 effect totals, effect-set digest, and v2
   cutpoint digest;
5. constructs v3 policy by preserving every legacy field and importing only the
   two device fields;
6. drops only the legacy metadata table;
7. creates the exact v3 metadata table;
8. inserts recomputed v3 metadata over the unchanged effect rows;
9. verifies the complete exact v3 schema;
10. reloads and re-attests v3 state; and
11. compares retained rows, generation, and full migrated limits before commit.

SQLite documents that `BEGIN IMMEDIATE` starts a write transaction immediately,
and that an explicit transaction persists until `COMMIT`, `ROLLBACK`, or an
error that provokes rollback:
https://sqlite.org/lang_transaction.html

SQLite's atomic-commit contract is that all changes in one transaction occur or
none do, including under crash recovery (with WAL using a different mechanism
than rollback-journal mode):
https://sqlite.org/atomiccommit.html

The compiled fault-injection test installs a temporary SQLite authorizer that
denies the v3 metadata `INSERT` after the old table has been dropped and the new
table created. SQLite documents that the authorizer is invoked while statements
are prepared and can return `SQLITE_DENY`:
https://sqlite.org/c3ref/set_authorizer.html

After the injected failure, the connection observes the exact v2 schema again.
A later clean migration succeeds. This proves the application's transaction
scope for this failure frontier; it is not a substitute for SQLite's own power-
loss test suite or a custom-VFS crash campaign.

## Copy-frontier refactor

The audit also found a concrete waste regression in the recovered branch. A
newly admitted request could create:

1. a temporary canonical-operation string;
2. a temporary payload string;
3. copies of both into `StoredEffect`; and
4. another complete `StoredEffect` copy into the sorted vector.

Rev0889 now encodes and copies directly into one local `StoredEffect`, then moves
that object into the retained vector. Derived actor/device usage and digest
strings are moved into the loaded snapshot. Internal mutation paths request an
`AuthorityOnly` projection, avoiding construction of an O(history) public
record vector that no caller observes. Only `snapshot_or_throw()` requests the
`PublicSnapshot` projection, and that boundary moves each already-validated
record into the returned snapshot.

This does not make the owner scalable. Each operation still restores all rows,
loads all payload bytes, revalidates canonical operations, hashes the complete
retained closure, and builds actor/device maps. It remains an intentionally
expensive correctness oracle.

## Executable evidence

The owner tests cover:

- three retained actor epochs across two device IDs;
- exact actor and device counts, staged/published partition, and bytes;
- v2 fixture construction with the exact legacy schema and legacy digest domain;
- migration preserving every legacy policy field despite conflicting caller
  defaults;
- importing only the two new device limits;
- a changed v3 cutpoint with unchanged retained effect authority;
- duplicate reconciliation under a newly saturated cap;
- device-count rejection across actor epochs with folder headroom;
- device-byte rejection distinct from count and folder limits;
- independent-device admission;
- persisted device policy surviving restart with conflicting defaults;
- invalid migration policy failing before DDL;
- tampered v2 cutpoint failing before DDL;
- post-DDL fault injection rolling back to exact v2;
- successful retry after rollback; and
- v3 device-usage-digest tamper rejection on restart.

The file-delivery integration test additionally proves that an older actor epoch
of the authenticated sender device can saturate only that device while folder
capacity remains available. Receiver-local diagnostics identify
`DeviceEffectCount`, but no causal evidence or materialization authority is
created and the wire receipt remains the generic nonterminal capacity class.
The sender then releases the exact claim to its own bounded retry schedule.

## Severe remaining gaps

### Payload bytes are not total storage cost

The quotas charge retained payload bytes and effect count. They do not directly
charge canonical-operation bytes, SQLite page/WAL overhead, indexes, filesystem
block rounding, temporary publication files, or future chunk metadata. Global
operation-size and effect-count limits keep the model finite, but a zero-byte
payload can still carry a large bounded canonical operation. Production storage
admission needs an explicitly defined charge model and observed disk-pressure
policy; a raw payload-byte counter is not a disk quota.

### No protected reserve or fair scheduler

Per-device hard caps stop one already-known device from consuming the entire
configured folder budget, but they do not reserve headroom for a minimum number
of other devices, prioritize pending terminal reconciliation, or schedule fairly
when multiple identities compete. A large number of enrolled device IDs can
still exhaust the folder cap.

### No reclamation authority

Staged and published rows consume capacity indefinitely. There is no causal
stability, compaction checkpoint, offline-member/rejoin policy, collectible
state, or audited garbage-collection transition. Raising limits postpones the
same terminal condition; deleting by age or LRU would let a cache heuristic
rewrite exact authority.

### No pre-payload reservation

The current TLS request contains the complete bounded payload before durable
service admission. Device disk limits do not bound unauthenticated handshake
cost, authenticated in-flight memory, whole-frame buffering, or concurrent
session pressure. A production protocol needs a small authenticated offer,
idempotent durable reservation, bounded chunk transfer, and independently
owned listener/handshake/session limits.

### Policy provenance is local

The v2 migration imports the two new fields from constructor policy. The durable
v3 row thereafter owns them, but this revision does not authenticate an
operator-signed policy artifact, record policy provenance, or coordinate policy
across replicas. Deployment code must treat migration configuration as a
high-authority input.

## Recommended next correction

Keep this owner as the oracle and introduce a separate indexed admission owner
with:

- a durable membership-principal and policy epoch;
- exact per-principal and folder charges covering payload, canonical metadata,
  and reservation overhead;
- idempotent operation reservations before payload transfer;
- a protected reserve and fair eligible-work scheduler;
- typed dead-letter/operator replay authority; and
- differential, restart, and crash-frontier tests against the full-history
  implementation.

Do not add payload deletion until causal stability, compaction, rejoin, and
terminal receipt obligations jointly produce an executable collectible proof.

## Nonclaims

This audit and its lexical companion do not prove allocator behavior, database
power-loss safety, hash collision resistance, fair scheduling, membership
security, network confidentiality, filesystem free-space accounting, or package
integrity. Those claims require compiled runtime tests, sanitizers, crash/VFS
fault injection, protocol analysis, and sealed package verification.

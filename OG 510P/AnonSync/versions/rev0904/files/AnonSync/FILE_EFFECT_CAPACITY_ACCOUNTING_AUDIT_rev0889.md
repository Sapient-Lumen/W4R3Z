# File-effect capacity accounting and copy-frontier audit — rev0889

## Executive finding

The receiver file-effect owner had finite folder-global count and payload-byte
limits, but a rejection exposed only `CapacityBlocked`. Operators and future
schedulers could not identify the exact exhausted resource, attribute retained
usage to the incoming actor/device, or bind the observation to one durable
cutpoint. The stage path also performed avoidable full-payload and canonical
copies after authorization.

Rev0889 adds exact local accounting, persists a schema-v3 device-isolation
policy and compact derived witnesses, and defers retained-row construction until
all no-mutation decisions are complete:

- every load derives usage by exact `(device_id, epoch)` and by `device_id` from
  the complete retained row closure;
- schema v3 binds per-device count/byte limits, device count, and a
  device-usage digest into the durable cutpoint;
- capacity diagnostics identify the first violated folder/device constraint and
  include subtraction-safe budgets bound to the inspected generation/cutpoint;
- exact duplicates reconcile before quota enforcement;
- the delivery service retains detailed accounting locally but emits only the
  existing generic `EffectCapacityBlocked` wire disposition; and
- mutation paths avoid a redundant O(history) public snapshot projection and
  move insertion/attestation objects instead of copying them.

The exact migration and device-isolation review is in
`FILE_EFFECT_DEVICE_ISOLATION_MIGRATION_AUDIT_rev0889.md`.

## Exact authority model

### Rows are authority; summaries are checked projection

Canonical operation bytes, payload bytes, effect state, and transition
metadata remain the primary retained authority. The owner decodes, hashes, and
validates every row on every operation. Actor/device vectors are reconstructed
from that closure and sorted deterministically by ordered maps.

Schema v3 persists `device_count` and `device_usage_digest` as witnesses, not as
independent counters. A load recomputes and compares both before exposing a
snapshot or authorizing mutation. The cutpoint digest covers the persisted
folder policy, the per-device policy, state totals, effect-set digest, and
usage digest. A cached value cannot grant capacity by itself.

### Actor epoch and device identity stay distinct

`SyncReplicaFileEffectActorUsage` keys the complete actor namespace. Epoch
rotation therefore remains observable. `SyncReplicaFileEffectDeviceUsage`
separately aggregates every retained actor epoch with the same `device_id` so a
new epoch cannot reset a charge.

`device_id` is not silently promoted to a person, account, organization, or
membership principal. Enrollment and membership authority remain outside this
owner. A party able to acquire arbitrary new device IDs can evade this specific
boundary; the folder cap remains the final aggregate limit.

### One diagnostic owns one exact cutpoint

`SyncReplicaFileEffectStageOutcome` carries a
`SyncReplicaFileEffectCapacityBlock` only for `CapacityBlocked`. The block owns:

- `state_generation` and `cutpoint_digest`;
- the exact first violated constraint;
- folder effect-count and retained-payload budgets;
- device effect-count and retained-payload budgets;
- current usage for the incoming actor epoch; and
- current usage aggregated across its device epochs.

The budgets reuse subtraction-first `SyncReplicaResourceBudget::would_exceed()`
so an attacker-selected incoming charge cannot wrap addition. They are computed
under the same `BEGIN IMMEDIATE` transaction that restored and attested the
complete state. A rejection re-proves root authority, commits no mutation, and
returns the bound observation.

The local block is intentionally not serialized. Detailed receiver usage must
not become peer telemetry or let a receiver choose sender retry timing. The
sender validates only the generic nonterminal receipt and derives its retry
cutpoint from local persisted policy and its owned clock.

## Deterministic admission precedence

After canonical operation/payload validation and receiver-local path policy, the
stage path performs:

```text
exact duplicate
folder effect count
folder retained payload bytes
device effect count
device retained payload bytes
new-row construction and insertion
```

Folder constraints take precedence when multiple boundaries are exceeded. This
keeps the aggregate safety explanation stable while still exposing device
isolation when folder headroom exists. An exact duplicate is returned before
all capacity checks because it adds no retained bytes or row and is essential to
ambiguous-response recovery.

Existing rows that predate a stricter device policy remain canonical even if
their device is already over cap. The owner blocks only future unique admission;
it never deletes or rewrites evidence to make a new limit appear satisfied.

## Allocation and projection refactor

The prior insertion path could create temporary canonical/payload strings, copy
them into `StoredEffect`, then copy the complete object into the sorted vector.
The recovered branch also built a complete public effect-record projection for
internal mutations that never returned it.

Rev0889 changes the frontier to:

```text
validate canonical operation and payload size/digest
check local path capability
compare exact duplicate against caller-owned payload span
construct folder/device budgets
return no-mutation diagnostic when blocked
encode directly into one StoredEffect
copy payload span once into that StoredEffect
move StoredEffect into the retained vector
insert, derive, persist, reload, and re-attest
```

Derived actor/device vectors and digest strings move into the loaded snapshot.
Internal constructor/stage/materialize paths request `AuthorityOnly`; only
`snapshot_or_throw()` requests `PublicSnapshot`, where validated effect records
are moved into the returned view.

The delivery service stages from its decoder-owned request and then moves the
payload-bearing request into the inbound result. Compile-time nothrow-move
checks fence the post-stage ownership transfer.

This does not eliminate whole-frame buffering, payload hashing, one canonical
encoding used by shared operation validation, SQLite row restoration, or the
one retained payload copy required for a new row. The owner remains an
O(history) correctness oracle.

## Runtime evidence

Compiled owner tests cover:

- exact actor/device staged, published, count, and byte partitions;
- multiple actor epochs sharing one device;
- restart-identical projections and digests;
- exact duplicate reconciliation while limits are saturated;
- folder-count and folder-byte violations with stable precedence;
- device-count and device-byte violations with folder headroom;
- independent-device admission;
- no mutation on every rejection;
- exact v2-to-v3 migration and persisted policy restart;
- injected post-DDL migration rollback; and
- device-usage-digest tamper rejection.

The service integration test covers both aggregate and device-only pressure. In
the device case, an older epoch of the authenticated sender device consumes the
local quota. The receiver returns detailed `DeviceEffectCount` accounting,
creates no causal evidence or materialization authority, emits the generic wire
receipt, and the sender releases exactly the current claim under local bounded
backoff.

`tools/audit_sync_file_effect_capacity_accounting.py` is a lexical hygiene
inventory for reviewed type shape, ordering, test presence, build registration,
and release retention. It cannot prove C++ allocation behavior, SQLite
isolation/durability, hash strength, fairness, crash safety, membership security,
network privacy, or package integrity.

## Remaining severe gaps

The change improves isolation but does not make the receiver self-healing:

- staged and published payloads consume capacity indefinitely;
- no stable membership principal or policy provenance is authenticated;
- no protected reserve or fair scheduler exists across many device IDs;
- payload bytes are not total disk cost—canonical bytes, SQLite/WAL/index
  overhead, filesystem block rounding, and temporary files are not directly
  charged;
- no durable pre-transfer reservation bounds whole-frame network/memory work;
- no dead-letter, expiry, operator replay, or reclamation owner exists; and
- no causal-stability, compaction, offline-device rejoin, or collectible proof
  authorizes deletion.

The deeper lifecycle plan is in
`RECEIVER_STAGING_FAIRNESS_AUDIT_rev0889.md`. The safe next step is a separate
indexed admission/reservation owner, differentially tested against this oracle,
with durable membership-policy epochs and an explicit total-resource charge
model. Payload reclamation must wait for executable causal stability and rejoin
semantics.

## Nonclaims

Rev0889 does not claim fair resource allocation, anonymity, Sybil resistance,
filesystem free-space enforcement, production scalability, or exactly-once
network delivery. It proves a narrower boundary: exact retained history derives
and binds deterministic folder/device accounting, unique admission cannot
cross the configured first violated limit, exact retry remains idempotent, and
receiver-local detail does not become peer authority.

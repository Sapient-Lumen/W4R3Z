# AnonSync rev0804 — source-first transfer, exact schema lifetime, and focused proof ownership

## Lineage

Rev0804 is prepared from the complete verifier-clean archive
`AnonSync-rev0801-2026.07.15.17.05-forklineage-processauthority-parentcleanup-lineagetruth.zip`,
SHA-256 `9f96e2230a804fa844cc9535acd3867fa1e3cbe5b8da5abbb4780bf97cf482e2`.
That archive passes all 24 checks in its own release-package verifier.

The previously linked rev0802 and rev0803 artifacts were not present as usable
source archives in the cloudtainer. A surviving rev0803 work directory had no
source differences from rev0801 and omitted historical evidence files, so it
was treated as untrusted recovery input rather than a lineage parent. The
verified rev0801 package is the byte-authoritative source basis. This revision
number intentionally preserves the conversational sequence without pretending
that missing archives were verified parents.

## Heart of the mission

AnonSync is an **evidence-authorized convergence engine**. Observation is not
authority. A copied pointer, successful callback, open handle, matching path,
returned row, signature result, PID, or reported schema can be useful evidence;
it cannot authorize a transition until the owning boundary proves the exact
content, provenance, process, generation, lifetime, policy, relationship,
resource, and durability conditions.

Rev0804 adds a related transition rule:

> Validate and escrow incoming authority before destroying outgoing authority.

A fail-stop that happens only after an unrelated resource has closed, finalized,
rolled back, unlinked, or called application code is not a source-first denial.

## Severe defect 1: invalid move sources caused valid destination side effects

`ProcessBoundHandleSlot::operator=()` previously executed this order:

1. dispose the destination;
2. inspect the source;
3. transfer the source state.

`SyncSqliteStmt::operator=()` similarly reset the destination statement and
database-generation pin before the complete source object had been validated.

That is observably unsafe because SQLite destruction is executable behavior.
`sqlite3_close()` can run application-defined function destructors, while
`sqlite3_finalize()` releases bound values through their registered
destructors. A fork-inherited source had no child authority, but it could still
cause a freshly created child-local destination to execute those callbacks
before AnonSync exited with status 86.

The preserved parent behavior is:

```text
database_move_exit=86
database_destination_disposed_before_rejection=true
statement_move_exit=86
statement_destination_disposed_before_rejection=true
```

Rev0804 records:

```text
database_move_exit=86
database_destination_disposed_before_rejection=false
statement_move_exit=86
statement_destination_disposed_before_rejection=false
```

### Correction

Database and statement ownership transfer now follows:

1. validate the complete source without side effects;
2. validate the destination;
3. move the source capability into local escrow, emptying the caller-visible
   source object;
4. dispose the destination;
5. install the escrowed source.

`ProcessBoundHandleState` now owns a lifecycle-locked `disposal_pending` state.
The exact shared generation remains alive while `sqlite3_close()` or
`sqlite3_finalize()` executes. Any callback or concurrent operation that tries
to inspect, borrow, refill, reset, move, or destroy that owner while disposal is
in flight fails stopped before mutation. After SQLite returns, the transition
revalidates the empty state and clears the fence.

The focused executable covers seven adversarial classes:

- inherited database source;
- inherited statement source;
- output-pending source;
- database-close callback reentry;
- statement-finalize callback reentry;
- close callback attempting to mutate the moved-from database source; and
- finalize callback attempting to mutate the moved-from statement source.

It passes 40 checks. The architecture audit passes 17/17.

## Severe defect 2: schema attestation did not own its connection generation

`PeerTransportIngressSchemaAttestation` retained a raw `sqlite3*` and a
connection-authorizer proof. That established neither C++ lifetime nor exact
owner generation. The typed owner reported zero retained borrows, and closing it
while the attestation remained live succeeded:

```text
attestation_owner_borrows=0
owner_close_exit=0
```

This allowed a process-local claim about one inspected connection to outlive the
owner that made the claim. Pointer equality cannot repair that gap because a
later connection may reuse an address, and a raw address cannot prevent close.

### Correction

The attestation now contains `SyncSqliteSerializedDbBorrow` and is explicitly
move-only. Initialization accepts `SyncSqliteDbHandleSlot&`, mints a borrow from
the exact owner generation used for schema inspection, and transfers that pin
into the returned attestation. Use-time verification borrows the candidate owner
and matches both handle and generation before acquiring the authorizer lease.

Current behavior is:

```text
attestation_owner_borrows=1
owner_close_exit=86
```

Move transfers the single retained pin; it does not duplicate or release it.
Write/read connection member order is owner, attestation, use borrow, so reverse
destruction releases use authority, then the attestation pin, then the owner.
The schema proof passes 67 checks; the architecture audit passes 25/25.

## Refactor: schema proof no longer compiles the application monolith

The parent schema test was a separate source file but not a separate build
boundary. It exposed 40 first-party translation units and 56,044 lines,
including 29 core-like units and the 24,531-line `sync_domain.cpp`.

Rev0804 introduces:

- `anonsync_sha256_digest`, the sole owner of SHA-256 calculation and lowercase
  digest validation;
- `anonsync_peer_ingress_schema`, the focused owner of schema attestation,
  payload-store schema proof, and exact schema identity; and
- `sync_peer_ingress_payload_store_schema.cpp`, separating schema proof from
  payload data operations.

The core consumes these libraries instead of recompiling their source. A
duplicate `sync_sqlite_schema_identity.cpp` source-list entry was removed.
CMake configuration guards reject schema-source reabsorption and any focused
schema dependency on `anonsync_core_lib`.

Clean graph comparison:

| Metric | rev0801 | rev0804 |
|---|---:|---:|
| Ninja actions | 57 | 22 |
| First-party translation units | 40 | 13 |
| Exposed first-party lines | 56,044 | 4,846 |
| Core-like translation units | 29 | 0 |

This is a 91.4% reduction in exposed first-party lines for the schema proof.

## Validation

Completed gates:

- GCC 14.2 Debug, bundled SQLite 3.53.3, `-Werror`: complete build.
- Full CTest: **67/67 passed**.
- `anonsync_sqlite_source_first_move_test`: **40 checks**.
- `anonsync_sqlite_owner_generation_borrow_test`: **271 checks**.
- `anonsync_peer_ingress_schema_attestation_test`: **67 checks**.
- GCC 14 ASan/UBSan focused lane: **3/3 passed**.
- Clang 17 focused lane with `-Wall -Wextra -Wpedantic -Wconversion
  -Wsign-conversion -Wshadow -Werror`: **3/3 passed**.
- GCC 14 focused first-party `-O3 -DNDEBUG -Wall -Wextra -Wpedantic
  -Werror`: **3/3 passed**. The bundled SQLite C amalgamation was compiled at
  `-O0` in this lane to avoid representing third-party optimization cost as a
  first-party proof.
- Source-first architecture audit: **17/17**.
- Schema owner-generation/build-boundary audit: **25/25**.
- Process-authority audit: **83/83**.
- Parent rev0801 package: **24/24** verifier checks.

No full-core sanitizer claim is made. No complete optimized Release build or
optimized bundled-SQLite claim is made.

## What remains missing or wasteful

### Priority 0 — crash-cut protocol oracle

A valid SQLite database can still encode an invalid AnonSync recovery outcome.
The next high-leverage boundary is a custom fault-injecting VFS plus a domain
oracle that interrupts each write/sync/truncate/lock/rename/publication edge,
restarts in a separate process, and checks both SQLite integrity and permitted
protocol state. Database, WAL/journal, receipts, checkpoints, staging files,
sidecars, and filesystem publication must be tested as one recovery system.

### Priority 0 — disposable hostile-database worker

The snapshot geometry and progress/row/text/time budgets are valuable but do not
bound SQLite allocator behavior, recursive parser cost, operating-system
resources, or every extension surface. Untrusted interpretation should move to
a disposable worker with CPU, address-space, file-size, descriptor, syscall,
namespace, and wall-clock limits. The parent should accept only a small typed
result, not a live SQLite capability.

### Priority 0 — explicit privacy and key-lifecycle model

AnonSync currently proves authentication and exact local persistence more
strongly than anonymity or confidentiality. The design must state who the
adversaries are; which payloads and metadata are visible; how devices enroll;
how epochs rotate; what revocation, recovery, forward secrecy, and
post-compromise recovery mean; and how secrets are held and erased in memory.
MLS is relevant research for group key epochs and post-compromise properties,
but it is not a drop-in claim for this system.

### Priority 1 — executable convergence algebra

Manifests, tombstones, idempotency keys, lineage, conflict copies, receipts, and
checkpoints are mechanisms, not yet a formal convergence contract. Each
operation should be classified by commutativity, idempotence, monotonicity,
causal dependence, and coordination requirements. Generated traces should
exercise duplication, loss, reordering, partitions, concurrent update/delete,
clock skew, restart, and key-epoch changes against a reference model.

### Priority 1 — continue extraction by invariant ownership

`sync_domain.cpp` remains 24,531 lines; `sqlite_replay_ledger.cpp` 5,312;
`reporting_selftests.cpp` 4,509; and `sync_peer_ingress_lifecycle.cpp` 3,831.
The next extractions should isolate checkpoint/recovery state, replay-ledger
snapshot/signing logic, and lifecycle transitions only where each boundary has
an independently testable invariant. Splitting for file count alone would add
indirection without proof.

### Priority 1 — retire raw SQLite compatibility surfaces

Typed owner-generation proofs cannot cover code that freely decays to
`sqlite3*` or `sqlite3_stmt*`. Migration should remain monotone: isolate one
boundary, preserve a pre-fix executable, add direct sanitizer/strict lanes and a
build guard, then remove the raw path after parity testing.

## Research-informed speculation

A content-addressed evidence DAG could eventually unify immutable lineage,
partial synchronization, deduplication, and restart discovery. A digest must
remain evidence rather than authority: it does not prove truth, freshness,
policy permission, signer authorization, non-revocation, confidentiality,
availability, or non-equivocation. An authoritative node would need to bind
content digest, signer/key epoch, policy version, subject, generation,
preconditions, predecessor set, and revocation context.

Formal CRDT results are useful for stating convergence conditions, but AnonSync
should not call its current state a CRDT merely because it has replicas and
conflict handling. Some operations may be order-sensitive or coordination
requiring; the executable algebra should make that explicit.

Official and primary references used for this review are preserved in
`REVISION_EVIDENCE/rev0804/research/ONLINE_RESEARCH.md`.

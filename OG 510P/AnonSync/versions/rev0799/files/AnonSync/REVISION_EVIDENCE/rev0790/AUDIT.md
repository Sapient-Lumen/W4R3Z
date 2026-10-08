# rev0790 deep audit — durable values must not be normalized into authority

## The heart of the mission

AnonSync is an **evidence-authorized convergence engine**. Its governing rule is
not merely “validate inputs”; it is **do not strengthen or discard evidence while
moving it across a boundary**.

A transport response does not prove acceptance. A pointer does not prove owner,
process, thread, generation, or lifetime. A successful SQLite call does not
prove media durability. A declared SQL type does not prove the storage class of
a particular value. A TEXT pointer does not prove the number of bytes. A hash
verifies only the exact byte sequence supplied to the hash function.

The intended transition is:

1. observe without silently normalizing;
2. preserve evidence and provenance;
3. validate at the owner of the invariant;
4. mint the narrowest process-local capability or durable record needed;
5. consume that authority only within its bounded lifetime; and
6. reconstruct authority after restart from durable evidence, never from a
   serialized live capability.

Rev0790 repairs a breach of step 2: SQLite's representation-conversion APIs were
allowed to alter durable evidence before verification.

## What had gone severely wrong

### Hidden bytes were outside the effective ledger hash chain

Production contained C-string reads equivalent to:

```cpp
std::string(reinterpret_cast<const char*>(sqlite3_column_text(stmt, col)))
```

SQLite TEXT may contain embedded NUL. That constructor authenticates only the
prefix. The preserved parent reproducer appends a NUL and hidden suffix to a
hash-bound `case_id` while leaving the stored entry hash unchanged. The old
snapshot verifier read the prefix, reproduced the old hash, and accepted a
database whose durable bytes did not match the bytes it claimed to verify.

This is a serious integrity failure: the database held one value while the
verifier authenticated another. Rev0790 preserves the explicit SQLite byte
count, so the suffix changes the hash input and fails closed.

### Dynamic numeric coercion laundered a REAL into an INTEGER

SQLite is dynamically typed. `sqlite3_column_int64()` converts REAL to INTEGER.
The parent verifier accepted `line_count=2.75` as `2`; the table's ordinary
INTEGER affinity did not prevent that stored REAL.

Rev0790 checks the value's initial storage class before representation access.
Wrong classes are rejected rather than converted. Schema spelling is now
supporting evidence, not a substitute for the observed value type.

### Nine convenience locations partially owned one trust transition

The parent production tree contained 80 direct scalar extraction calls in nine
files. Some checked types; some did not. Some preserved byte lengths; some used
C strings. Some treated NULL as empty. That was not nine harmless helpers; it
was nine partial owners of the same durable-evidence promotion rule.

Rev0790 centralizes the raw API in one invariant-owned library. Production now
has six direct calls in one file. The projection decoder retains field/map
semantics but delegates mechanics. A 30-check source audit fences text, blob,
byte-count, type, integer, floating, value-object, and UTF-16 result APIs.

## Why the refactor is architectural

`sqlite_exact_value` makes the SQLite trust boundary explicit. It verifies
current row, index, initial storage class, nullability, exact length, signedness,
and optional byte ceiling before producing a C++ value. Failures are typed and
value-free.

The target is independently linkable. Its focused proof needs six Ninja actions,
two first-party translation units, and 523 lines, versus 45 actions, 35 units,
and 53,355 lines for the core. CMake rejects reabsorption and reverse coupling.
This makes repeated sanitizer, warning, optimized, and fuzz lanes practical.

The source audit is monotone: any new raw production extraction outside the
owner fails the normal test suite. A favorable count has become an enforced
architecture rule.

## What the audit found beyond the fixed defects

### Statement lifetime/thread authority is not encoded in the reader type

The exact API still accepts `sqlite3_stmt*`. It checks row state immediately,
but the type does not prove that another thread cannot step, reset, or finalize
the statement between checks and extraction. SQLite defines such interference
as undefined. Function-local statements and AnonSync's serialized ownership
machinery currently provide the operational premise, but a future
thread-affine current-row borrow would make it explicit and mechanically
reviewable.

### Exact storage class is necessary but not semantic validation

`SQLITE_TEXT` does not prove valid application UTF-8, normalization, canonical
path spelling, lowercase digest encoding, identifier grammar, or permitted
length. `SQLITE_INTEGER` does not prove a field-specific range or chronology.
Those checks must remain at semantic owners. A future constexpr/generated field
descriptor could bind storage class, nullability, byte/range limits, schema
epoch, sensitivity, and semantic validator, provided generated output remains
reviewable and independently tested.

### Resource exhaustion is still open

Most TEXT reads use `maximum_bytes=0`, which intentionally means unlimited at
this layer. The untrusted snapshot verifier already applies defensive,
query-only, untrusted-schema, ATTACH, trigger-depth, variable-number, and SQL-
length restrictions, but it lacks a complete versioned resource profile for
cell/row length, columns, page/file size, VM operations, elapsed time, and heap.
A malicious but structurally valid file can still consume resources before
semantic rejection.

### Monolithic structure still wastes verification capacity

A full sanitizer core build was resumed across four command windows and still
remained in `sync_domain.cpp`. That is not a sanitizer finding, but it is direct
evidence that unrelated authority domains are coupled so broadly that an
important verification lane becomes impractical. The focused ASan/UBSan lane
passed. Further extraction should follow invariant ownership, not arbitrary
file splitting.

## Highest-priority missing work

### P0 — crash-cut state oracle

Build a fault-injecting VFS and protocol oracle. Cut every write, sync, truncate,
rename, lock, journal/WAL, checkpoint, sidecar, staging, conflict-copy, receipt,
and checkpoint-publication boundary. Reorder or corrupt only writes that were
not made durable. Restart in a separate process. Verify both:

1. SQLite structural integrity; and
2. whether the combined database/filesystem state is one of AnonSync's
   explicitly permitted outcomes.

A clean `integrity_check` is not enough if a final file is published without its
receipt, a checkpoint advances without its sidecar, or a conflict copy and
ledger disagree.

### P0 — explicit privacy and adversary model

The code has substantial authentication, replay, trust-profile, key-ID, and
signature machinery. That is not an anonymity or confidentiality proof. Define
which adversaries observe servers, peers, endpoints, timing, sizes, filenames,
manifests, conflict history, local databases, memory, logs, and backups. Then
specify content encryption, metadata leakage, enrollment, key epochs, rotation,
revocation, recovery, forward secrecy, post-compromise recovery, and secret
zeroization/locked storage.

### P1 — executable convergence contract

Classify every operation as commutative/order-sensitive, idempotent/single-use,
monotone/retracting, causally dependent/independent, and locally decidable or
coordination-requiring. Compare the C++ implementation with a small reference
model under duplicate, omission, reorder, retry, partition, concurrent
edit/delete, clock skew, restart, and key-epoch traces.

Manifests, lineages, tombstones, conflict copies, receipts, workorders, and
checkpoints are mechanisms. They do not by themselves prove strong eventual
consistency, and AnonSync should not be called a CRDT without stated merge laws
and delivery assumptions.

### P1 — versioned STRICT and resource migration

Move eligible tables toward STRICT schemas or explicit `typeof()` and range
constraints through versioned migrations. Retain exact read-time checking for
legacy/hostile files and because STRICT still performs lossless coercion. Bind a
separate untrusted-snapshot resource profile to measured protocol maxima and
exercise it with boundary and oversized corpora.

### P1 — continue decomposition by invariant ownership

Likely next extraction candidates are replay-ledger read-only verification and
trust evaluation, checkpoint repository/transaction families in
`sync_domain.cpp`, ingress lifecycle state transitions, and fixtures embedded
in production-scale selftest sources. Each extraction should have a narrow
interface, no reverse core dependency, an adversarial focused proof, and a
measured graph reduction.

## Speculative direction: an evidence DAG, not hash authority

A content-addressed causal DAG could unify immutable lineage, idempotency,
snapshot discovery, partial synchronization, and externalized historical packs.
A hash pointer proves relationship to exact bytes. It does not prove truth,
authorization, freshness, confidentiality, availability, policy compliance, or
non-equivocation. Nodes would still need signer/key epoch, policy version,
subject, generation, predecessor/precondition set, and revocation context. The
DAG may carry evidence; it must never mint authority merely by existing.

## Proof boundary for this revision

Rev0790 proves, for the tested projection, that migrated production has one raw
SQLite scalar conversion owner; focused readers reject wrong storage classes,
invalid row/index state, negative unsigned values, NULL/empty confusion,
embedded-NUL loss, and configured byte-limit violations; the two preserved
integration attacks are rejected; and all required tests/audits pass.

It does not prove malicious-VFS resistance, media durability, complete resource
containment, statement-race safety at the type level, formal convergence,
Byzantine safety, end-to-end privacy, or deployment fitness.

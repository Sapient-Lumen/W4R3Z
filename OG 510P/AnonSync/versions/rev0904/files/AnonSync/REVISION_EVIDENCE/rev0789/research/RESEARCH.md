# rev0789 research record and design speculation

Captured 2026-07-15 UTC. Primary sources were preferred. The observations below
inform design direction; speculative proposals are labeled and are not claims
about properties AnonSync already has.

## Boundary authority and end-to-end correctness

**Saltzer, Reed, and Clark, “End-to-End Arguments in System Design.”**
https://web.mit.edu/saltzer/www/publications/endtoend/endtoend.pdf

The paper's central design argument is that functions such as duplicate
suppression, delivery acknowledgment, and crash recovery often require
application-end verification; lower layers may improve performance but cannot
fully establish the end condition. This is the closest conceptual ancestor of
AnonSync's mission. AnonSync should keep making each authority statement at the
highest boundary that has enough context, while treating lower-layer evidence as
useful but insufficient.

## SQLite row-state contract

**SQLite, “Result Values From A Query.”**
https://sqlite.org/c3ref/column_blob.html

SQLite states that column APIs are valid only while the most recent step
returned `SQLITE_ROW`; use after reset/finalize or any other step result is
undefined. The page also documents TEXT/BLOB conversion and byte-count rules.
This directly motivated the `statement_not_positioned` gate and text-before-byte
extraction in rev0789.

**SQLite, “Number of columns in a result set.”**
https://sqlite.org/c3ref/data_count.html

`sqlite3_data_count()` reports columns in the current row and returns zero when
no result is ready or after `SQLITE_DONE`. For AnonSync's fixed twelve-column
SELECT projection, equality with `sqlite3_column_count()` is a public,
non-invasive row-position observation before value access.

## Crash and I/O-failure testing

**SQLite, “How SQLite Is Tested,” sections on I/O errors and crash testing.**
https://sqlite.org/testing.html

SQLite's own tests inject I/O failures, run crash work in another process, use a
special VFS to reorder/corrupt unsynchronized writes, reopen the database, check
that changes completed or rolled back, and run `PRAGMA integrity_check`. AnonSync
needs an analogous protocol oracle covering its database, sidecars, staging
files, receipts, and checkpoint state—not merely SQLite integrity.

**SQLite, “Standard File Control Opcodes.”**
https://sqlite.org/c3ref/c_fcntl_begin_atomic_write.html

Useful observations include `SQLITE_FCNTL_HAS_MOVED`, file/VFS pointers, sync and
commit-phase notifications, and platform-specific native handles. These can
strengthen path/descriptor identity and instrumentation, but they do not by
themselves prove storage honesty or durability.

## Coverage-guided fuzzing

**LLVM, “libFuzzer — a library for coverage-guided fuzz testing.”**
https://llvm.org/docs/LibFuzzer.html

LLVM specifies the `LLVMFuzzerTestOneInput` interface and recommends narrow,
fast, deterministic targets that tolerate arbitrary input. `-fsanitize=fuzzer`
provides instrumentation and the driver and can be combined with sanitizers.
Rev0789 follows that shape by directly instrumenting the small decoder and
canonical verifier rather than the complete application.

## Local-first goals and privacy

**Kleppmann et al., “Local-first software: You own your data, in spite of the
cloud.”** https://www.inkandswitch.com/essay/local-first/

The local-first ideals include offline operation, multi-device collaboration,
long-term preservation, privacy/security by default, and user ownership. AnonSync
already invests heavily in offline/restart evidence and peer reconciliation, but
must add an explicit confidentiality/metadata/key model before claiming the
privacy half of that vision.

## Formal convergence

**Shapiro et al., “Conflict-free Replicated Data Types,” INRIA Research Report
RR-7687.** https://hal.inria.fr/docs/00/60/93/99/PDF/RR-7687.pdf

CRDT convergence is a formal property under stated conditions, not a synonym for
having retries, idempotency keys, or conflict files. AnonSync should specify its
state, partial order, operations, delivery assumptions, and sufficient
convergence conditions, then test them against an executable model.

## Content-addressed causal evidence

**Sanjuan et al., “Merkle-CRDTs: Merkle-DAGs meet CRDTs.”**
https://arxiv.org/abs/2004.00107

The paper studies Merkle DAGs as transport/persistence and logical-clock support
for convergent data types under weak messaging guarantees, with content-addressed
deduplication. **Speculation:** AnonSync could represent durable transition
evidence as content-addressed causal nodes and exchange missing subgraphs. This
could unify lineage, idempotency, partial replication, and evidence retention.
It would not eliminate authorization: hashes bind bytes, while AnonSync still
needs signer, policy, key epoch, subject, precondition, revocation, availability,
and confidentiality rules.

## Resulting research program

1. Build a deterministic crash-cut harness and protocol state oracle.
2. Write an adversary/privacy specification before selecting encryption.
3. Extract an executable convergence model and generate schedule traces from it.
4. Prototype a signed, policy-bound evidence DAG only after the first three make
   its node semantics precise.
5. Treat build-graph size, sanitizer frequency, and evidence-pack size as
   correctness metrics because they determine what can be continuously proved.

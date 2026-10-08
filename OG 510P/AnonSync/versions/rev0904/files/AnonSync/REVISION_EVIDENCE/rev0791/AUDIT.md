# rev0791 deep audit — restart must reconstruct replay authority from row truth

## The heart of the mission

AnonSync exists to converge replicas without laundering observations into
authority. The durable restart boundary is where that mission is easiest to
violate: once bytes are in a database, ordinary code tends to treat successful
queries, schema declarations, and familiar-looking strings as proof. They are
not. Restart must independently reconstruct every authority-bearing relation.

For integrated sender replay, the relevant claim is not merely “a row exists.”
The claim is that exact, bounded evidence from an authenticated ingress boundary
is fresh, unique in the protocol's scope, and atomically associated with the
prepared effect that was independently reconstructed from the decision chain.

## What had gone severely wrong

### A whole durable authority table escaped semantic reload verification

Rev0790 checked the expected replay-cache table and index names but never read
its rows during normal reload or snapshot restore. That left 15 columns of
security evidence outside the restart proof. Digests could have wrong case,
required integers could use coercible storage classes, principals could contain
hidden control bytes, timestamps could attack signed arithmetic, and a row could
reference the wrong prepared effect.

### Integrity checking was mistaken for relationship checking

SQLite explicitly documents that `PRAGMA integrity_check` does not find foreign
key errors. The preserved reproducer disables enforcement while tampering and
changes `prepared_sequence` to 999. Turning enforcement back on does not scan
old rows. Rev0790 reload therefore accepted an orphaned replay reservation.

This is mission-level failure: a historical row observation was promoted into
durable replay authority without proving its parent decision existed.

### Ephemeral staged nonce state survived reload

`reload_chain_or_throw()` rebuilt committed sets but did not clear
`staged_ingress_sender_replay_nonce_keys_`. Reusing a live ledger object for
reload could retain a nonce reservation that was never part of the newly loaded
durable state. Rev0791 clears it with the other staged sets before reconstruction.

## What changed

### One semantic owner

The new pure C++ owner is independent of SQLite. It validates values passed to
it and cannot open a database or acquire a statement. This makes malformed and
overflow-edge proofs cheap, deterministic, and reusable by staging and reload.
The 22-check source audit enforces the one-owner shape and both trust-path calls.

### Exact row acquisition and bounded fields

The integrated scanner uses the rev0790 exact-value boundary for every column.
TEXT and INTEGER must retain their initial SQLite storage classes; explicit byte
lengths preserve embedded NULs; digest and token fields have narrow ceilings;
principal is capped at 4096 bytes; nonce is capped at 128 bytes.

### Separate structural and semantic proofs

`foreign_key_check` rejects broken declared references. The scanner then verifies
more than SQLite can know: lowercase digest grammar, format version, token and
nonce alphabets, principal controls, replay-window policy, duplicate protocol
nonce identity, one replay row per prepared effect, and exact equality with the
reconstructed `(sequence, entry_hash, effect_idempotency_key)` tuple.

### Overflow-safe time logic

Checks branch on timestamp order and subtract the smaller from the larger. They
never compute `observed - window` or `observed + skew`, so hostile signed 64-bit
values cannot overflow. `INT64_MAX` equality and boundary windows are covered.

## Verification capacity and waste

The focused owner is 417 lines in 4 actions. The integrated test is
53,242 first-party lines in 47 actions and the core is 53,632
lines. The extraction makes semantic mutation roughly 128.61× smaller by line
exposure, but the integrated sanitizer lane still failed to finish building.
That is direct evidence that monolithic compilation is consuming assurance work.

## The most important remaining gap: valid substitution is still possible

The replay table is related to the prepared ledger row by a foreign key, but its
content is not included in the prepared entry's hash material. Rev0791 can reject
an orphan, malformed row, duplicate nonce, or mismatched tuple. It cannot prove
that valid-shaped replay evidence bound to an existing tuple is the *original*
evidence produced for that decision. A capable database modifier can potentially
substitute one valid row for another and choose a different existing prepared
tuple. The current hashes still verify because they never committed to the
replay evidence.

Deletion has a parallel ambiguity. Replay rows are pruned by time policy; an
absent row is not distinguishable from legitimate pruning without a durable
pruning record or authenticated accumulator.

The right correction is a new ledger material/schema version that commits to a
canonical replay-evidence digest, its uniqueness scope, and an auditable pruning
policy. Adding more string checks to the current row format would not solve
provenance.

## Other missing work

### P0 — crash-cut state oracle

Build a fault-injecting VFS and an AnonSync protocol oracle that cuts writes,
syncs, truncates, locks, WAL/journal publication, sidecars, staging files, and
checkpoints; restarts in a separate process; and distinguishes SQLite structural
integrity from a protocol-permitted combined database/filesystem state.

### P0 — explicit privacy and adversary model

Authentication and replay protection do not establish content confidentiality,
metadata privacy, forward secrecy, post-compromise recovery, or secret-memory
handling. The project name should not imply anonymity beyond an explicit, tested
adversary model.

### P1 — complete untrusted-snapshot resource profile

Per-field ceilings landed here, but total file/page size, row count, VM opcode
work, wall time, cache/heap, and allocation size remain incompletely bounded.
Use versioned limits and fail-closed compatibility tests rather than global
magic constants.

### P1 — runtime schema attestation

The read-only snapshot path inventories schema objects. Ordinary runtime open
still leans heavily on `CREATE ... IF NOT EXISTS`, profile rows, data scans, and
constraints. A shared exact schema owner would reduce divergence and reject
altered constraints/triggers/index definitions before any durable state is used.

### P1 — executable convergence contract

Classify each operation as commutative/order-sensitive, idempotent/single-use,
monotone/retracting, and causally independent/coordinated. Compare generated
partition, duplication, reorder, crash, delete/edit, and key-epoch traces against
a small reference model.

### P1 — continue invariant-owned decomposition

`sync_domain.cpp` remains over 24k lines and `sqlite_replay_ledger.cpp` now
contains multiple chains, outbox state, replay evidence, snapshots, restore, and
selftests. Extract only boundaries with separately expressible invariants; avoid
cosmetic file splitting.

## Proof boundary for rev0791

Rev0791 establishes exact and bounded replay-row semantics, foreign-key
verification, complete prepared-tuple equality, duplicate detection, overflow
safety, and one pure semantic owner on both restart and restore. It does not
claim replay-evidence provenance, pruning non-equivocation, full-core sanitizer
coverage, crash durability, bounded total resources, formal convergence,
Byzantine safety, or anonymity.

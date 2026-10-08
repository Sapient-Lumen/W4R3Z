# rev0789 deep audit — the heart, the breach, and the next architecture

## Heart of the mission

AnonSync is an **evidence-authorized convergence engine**. Its most valuable
idea is a discipline of epistemic boundaries: observations become authority
only after the owner of an invariant verifies the exact evidence required for
that transition. Live C++ capabilities bind process/thread/owner/generation and
lifetime. Durable records bind content, identity, idempotency, lineage, and
restart reconstruction. Neither is allowed to impersonate the other.

The mission is therefore: **converge replicas without laundering uncertainty**.
A successful transport call does not prove peer intent; an HMAC does not prove
confidentiality; a successful SQLite step does not prove durable media; a
pointer does not prove generation; equal strings do not prove independent
columns; and a local final state does not by itself prove global convergence.

## What had gone severely wrong

### 1. Undefined SQLite access was on an authority path

The row decoder could call the `sqlite3_column_*` family before a row existed,
after `SQLITE_DONE`, or after reset. This was not merely defensive-programming
debt: SQLite makes the result undefined. The pre-fix executable confirms that
an unstepped statement returned a successful projection in this toolchain.
Rev0789 establishes and tests a current-row precondition before reading values.

### 2. One value could masquerade as two evidence fields

The decoder accepted duplicate map indexes. A malicious or mistaken query/map
pair could omit one persisted field and reuse a different column. The pre-fix
reproducer demonstrates successful canonical verification of the forged
projection. Rev0789 requires a bijection from the twelve projection fields to
twelve distinct in-range result columns.

### 3. Focused tests were architecturally unfocused

Three small persistence boundaries were compiled through the whole core archive.
For each focused proof, 26 unrelated core translation units and the 24,530-line
domain sat on the critical path. This made clean sanitizer/optimized feedback
slow enough to discourage frequent use. Rev0789 moves invariant ownership into
three standalone libraries and installs configure-time anti-coupling guards.
The measured first-party C++ exposure falls 98.4–99.2%.

### 4. The “active implementation projection” omitted fuzz code

The package manifest was exact, but the supplementary projection used for the
claim “this is the tested implementation” excluded `fuzz/`. Rev0789 versions the
projection, binds fuzz sources, and makes the verifier recompute it. Release
truth should be derived from bytes, not asserted by a Boolean in
`RELEASE_GATE.json`.

## What is missing, in priority order

### P0 — crash-cut state oracle

Build an AnonSync VFS shim and state-machine oracle. Inject a crash or I/O error
at every write, truncate, rename, lock, and sync boundary; reorder/corrupt only
unsynchronized writes; restart in a separate process; then prove database
integrity and a protocol-specific outcome: wholly committed, wholly absent, or
recoverable from sufficient durable evidence. Exercise WAL, rollback journal,
sidecars, staging files, conflict copies, outbox rows, receipts, and checkpoints
together. This is the largest gap between “careful SQLite code” and a durable
convergence claim.

### P0 — explicit privacy/adversary model

The tree has authenticity and possession machinery (HMAC-SHA256, RS256, replay
and key IDs), but a source scan found no content-encryption or privacy layer.
The transport API carries `shared_secret` in two ordinary `std::string` fields.
Define who can observe endpoints, filenames, sizes, timings, peer IDs, manifests,
conflict history, SQLite files, memory, logs, and backups. Then define encryption
at rest/in transit/end to end, forward secrecy, key rotation/revocation,
recovery, zeroization/locked memory, and metadata minimization. Until that is
done, “Anon” should not be read as a proven anonymity or confidentiality claim.

### P1 — formal convergence contract

The code implements manifests, lineages, tombstones, conflict copies, transfer
receipts, checkpoints, workorders, reconciliation, and idempotency, but it does
not state a formal convergence algebra. Inventory every operation and classify
it as commutative, idempotent, monotone, causally ordered, or coordination
requiring. Write an executable small model and property tests for duplicate,
reorder, omission, retry, partition, concurrent edit/delete, clock skew, and
key-epoch change. Reserve “CRDT” for a design with stated and checked convergence
conditions.

### P1 — continue decomposition by invariant ownership

Do not split files merely to reduce line count. Extract complete boundaries with
small headers, explicit dependencies, their own adversarial tests, and no
reverse core dependency. The next candidates are checkpoint repository and
transaction families in `sync_domain.cpp`, replay-ledger signing/snapshot
sections, and selftest fixtures from `reporting_selftests.cpp`. Every extraction
should reduce a measured build graph and own a release audit.

### P1 — retire SQLite migration debt monotonically

The deterministic inventory still reports 40 raw opens, 70 raw transaction
control sites, 17 raw prepares, four `sqlite3_close_v2` calls, three raw-pointer
compatibility declarations, and one generic owner-borrow mint. Convert one
transaction family at a time to generation/process/thread/mutex-bound ownership,
then make the audit threshold decrease. New debt should be a configure or CI
failure.

### P2 — durable evidence graph

A content-addressed causal evidence DAG could deduplicate repeated receipts,
make lineage and partial synchronization explicit, and externalize historical
release evidence. However, a Merkle link proves content identity, not truth,
authorization, confidentiality, availability, or non-equivocation. Every node
would still need policy version, signer/key epoch, subject, generation,
preconditions, and revocation semantics.

### P2 — evidence-store hygiene and build economics

Historical evidence already exceeds active first-party source volume. Move old
revision packs to a content-addressed immutable store after proving every digest
is reachable; keep current evidence and retrieval roots in the source ZIP.
Cache or prebuild the pinned SQLite amalgamation for ordinary focused lanes, and
run its fully instrumented build in a dedicated upstream-boundary job.

## Architectural pressure map

- `src/sync_domain.cpp`: 24,530 lines;
- `src/reporting_selftests.cpp`: 4,498;
- `src/sqlite_replay_ledger.cpp`: 4,466;
- `src/sync_peer_ingress_lifecycle.cpp`: 3,833;
- `include/anonsync_core.hpp`: 3,499;
- `src/runner.cpp`: 2,198.

The public header and the domain unit are not only readability problems. They
create transitive recompilation, broad privilege surfaces, hidden dependency
cycles, and tests that accidentally prove far more—or less—than their names.
Rev0789 is a template: isolate by invariant, link production inward, link tests
directly, measure the graph, and reject re-coupling automatically.

## What rev0789 proves

It proves the corrected decoder fails before value access without a current row,
rejects duplicate/out-of-range maps deterministically, preserves empty text,
and remains stable under focused compiler/sanitizer/fuzzer lanes. It proves the
three focused targets no longer depend on the core. It proves the supplied
rev0788 archive and current v2 active projection are byte-accounted.

It does not prove media durability, malicious-VFS resistance, distributed
convergence, end-to-end privacy, Byzantine safety, key custody, or production
network deployment.

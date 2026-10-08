# Next work after rev0848

## 1. Unify SQLite callback registration

Create one typed, process-bound `SqliteConnectionCallbackRegistry` per connection
and migrate busy handler, progress handler, authorizer, trace hooks, and other
retained user-data registrations behind it. The registry should own setter
ordering, callback context lifetime, exact-generation borrows, detach, close,
and fork fail-stop behavior. Inventory every production call to callback setter,
`sqlite3_busy_timeout`, `PRAGMA busy_timeout`, `sqlite3_close_v2`, and raw close.

The key missing runtime property is replacement detection: SQLite has no busy
handler getter, so rev0848 currently relies on source confinement. A unified
registry should make the raw `sqlite3*` unavailable to code that can replace
callbacks.

## 2. Make teardown an explicit state machine

Represent `constructing -> live -> quiescing -> detached -> closed` as one typed
connection lifecycle. Quiescence should be proved by an executor or connection
lease, not only documented. Add deterministic races at every setter, callback,
detach, statement-finalization, strict-close, and close-v2 cutpoint. Add a
ThreadSanitizer lane once the surrounding test-process machinery is compatible.

## 3. Continue focused-test extraction

The five-line lifecycle driver avoids rebuilding unrelated corpora for Clang and
sanitizers. Apply the same pattern to other selftests that already live in
runtime libraries. Keep a small independent test for every advertised CLI flag,
and generate repetitive target/registration lists from checked data to reduce
CMake drift.

## 4. Build the cross-resource crash oracle

Model SQLite transactions, WAL/checkpoints, manifests, atomic files,
directories, recovery receipts, and downstream effects as one recovery state
machine. Generate crash cutpoints around every write, sync, rename, directory
barrier, checkpoint, and external effect. Compare recovery with a deterministic
reference model rather than accumulating only local source-shape audits.

## 5. Make convergence executable

Define operation semantics for update, delete, recreation, rename, concurrent
mutation, schema epoch, key epoch, and external effects. Classify operations by
idempotence, commutativity, monotonicity, causal dependence, and coordination
requirements. Generate duplicated, reordered, partitioned, retried, and
restarted histories and compare every replica with a compact reference model.

## 6. Specify privacy and key management

Do not infer anonymity from authentication or ledger integrity. Specify payload
encryption, membership, device generations, key epochs, rotation, revocation,
lost-device recovery, forward secrecy, post-compromise recovery, metadata
leakage, traffic analysis, backup custody, rollback resistance, and realistic
erasure limits.

## 7. Isolate hostile interpretation

Move hostile SQLite/document interpretation into disposable workers with sealed
descriptors, bounded request/response framing, CPU/memory/time/output/descriptor
limits, filesystem namespaces, syscall filtering, and explicit parent-side
verification. Treat seccomp and filesystem restriction as layers rather than a
complete sandbox.

## 8. Reduce monolith and evidence cost

Continue extracting invariant-owned C++ libraries from `sync_domain.cpp` and
focused tests from `sync_domain_selftests.cpp`. Historical evidence should remain
verifiable without being recursively copied into every ordinary development
handoff; consider a content-addressed evidence store plus a compact lineage
index.

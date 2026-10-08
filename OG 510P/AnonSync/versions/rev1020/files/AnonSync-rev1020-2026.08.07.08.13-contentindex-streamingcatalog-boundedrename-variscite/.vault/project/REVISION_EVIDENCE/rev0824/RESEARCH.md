# Rev0824 research notes

Rev0824 treats official SQLite documentation as a constraint and then checks the chosen interpretation with executable C++ oracles.

- SQLite transaction documentation states that `BEGIN IMMEDIATE` starts the write transaction immediately, that only one writer may exist at a time, and that a failed `COMMIT` can leave the transaction active for retry: <https://sqlite.org/lang_transaction.html>
- The changes-count API documents that `sqlite3_changes64()` reports direct changes only, excluding lower-level triggers and foreign-key side effects. Rev0824 therefore deletes in dependency order, attests the exact schema, and compares each direct row count instead of treating cascades as evidence: <https://sqlite.org/c3ref/changes.html>
- `SQLITE_FCNTL_HAS_MOVED` reports whether an open database file has been renamed, moved, or deleted since opening. Rev0824 combines that SQLite observation with guarded parent and database device/inode identity; neither alone is treated as complete namespace authority: <https://sqlite.org/c3ref/c_fcntl_begin_atomic_write.html>
- WAL mode makes the main database and WAL family a joint durability protocol. Reset therefore mutates the verified open database instead of deleting or replacing pathname members: <https://sqlite.org/wal.html>
- SQLite atomic-commit documentation distinguishes transactional commit from later external publication. Rev0824 consequently models receipt publication as a separate effect and carries a typed durable outcome if database commit succeeded before a later observer or publication failure: <https://sqlite.org/atomiccommit.html>

## Design inferences

An identity-only intent is insufficient. A ledger instance can advance while retaining the same identity, so a delayed request must bind the complete logical image it was authorized to erase. The canonical state digest covers every durable table, row, storage class, and value in stable order, while redundant counts and heads remain available for human review.

Path spelling is also insufficient. A different database can be placed at the same name after inspection. The request therefore binds lossless parent and database device/inode evidence, and the path guard re-inspects the current directory entry before returning its bound identity.

A successful `COMMIT` followed by a failed check is not a precommit denial. The API must retain the committed receipt and expose a recovery path rather than flattening both cases into one exception string.

## Speculative next work

1. Add a deterministic VFS crash-cut oracle spanning inspection, request publication, each SQL mutation, WAL sync, commit, postcommit checks, receipt atomic rename, and directory sync.
2. Persist or externally witness reset receipts where operational policy requires an audit trail that survives loss of both the request and the database.
3. Move hostile SQLite interpretation into a disposable worker with CPU, address-space, wall-clock, descriptor, syscall, and filesystem ceilings.
4. Generalize exact-state administrative capabilities to other non-monotone operations, including retention, revocation, and epoch migration.
5. Resume the independent convergence algebra and classify every replicated operation by commutativity, idempotence, monotonicity, causal dependency, and epoch compatibility.

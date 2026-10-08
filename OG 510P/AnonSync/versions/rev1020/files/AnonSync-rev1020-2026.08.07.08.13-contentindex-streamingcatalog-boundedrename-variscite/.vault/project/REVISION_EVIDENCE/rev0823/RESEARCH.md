# Rev0823 research notes

Rev0823 uses official SQLite documentation as a constraint, then checks the chosen interpretation with executable C++ oracles.

- SQLite's online-backup API defines a positive `N` as copying up to `N` pages and a negative value as copying all remaining pages. It also states that `sqlite3_backup_remaining()` and `sqlite3_backup_pagecount()` describe the most recent `sqlite3_backup_step()` call: <https://sqlite.org/c3ref/backup_finish.html>
- SQLite's backup overview explains that source changes between incremental steps can cause backup restart behavior, and that holding a read transaction on the source prevents the source database from changing for that reader's snapshot: <https://sqlite.org/backup.html>

## Design inference

A preflight and a postcheck do not bound the effect between them. The authority unit should therefore be one small copy step, not an entire database. The source snapshot, page policy, process incarnation, transaction state, reported page count, reported remaining work, and progress relation must all survive from one step to the next.

A pinned read snapshot is also stronger than repeatedly following the newest source. It gives the operation a stable semantic object: “copy this image.” Concurrent writers may continue in WAL mode, but they cannot silently enlarge or restart the authorized image.

## Speculative next work

1. Replace `load(reset=true)` with a receipt-bearing administrative reset protocol and remove the last ordinary SQLite-family deletion authority.
2. Add a deterministic VFS crash-cut oracle spanning snapshot pin, backup stepping, private canonicalization, serialization, atomic publication, directory sync, and postpublication sidecar checks.
3. Move hostile database interpretation into a disposable worker with CPU, memory, wall-clock, descriptor, syscall, and filesystem ceilings.
4. Generalize finite-effect owners into typed transition capabilities so every loop exposes its budget, progress measure, cancellation frontier, and cleanup evidence.
5. Build the independent convergence algebra previously identified: classify durable operations by commutativity, idempotence, monotonicity, causal dependency, and epoch compatibility, then differentially execute generated traces against production C++.

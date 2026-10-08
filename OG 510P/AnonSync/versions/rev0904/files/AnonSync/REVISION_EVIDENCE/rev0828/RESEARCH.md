# Rev0828 research notes

Primary SQLite documentation was used to distinguish the process-level oracle
implemented here from the stronger storage-fault oracle still missing.

## SQLite crash testing and VFS injection

SQLite's own test strategy uses alternative VFS implementations and crash-test
processes to inject I/O errors, simulate crashes, and check that transactions
commit or roll back cleanly. The journal-test VFS also observes write ordering
and atomicity assumptions. Rev0828 follows the process/reopen part of that
approach but does not yet interpose on every VFS operation.

- SQLite testing: https://sqlite.org/testing.html
- SQLite VFS overview: https://sqlite.org/vfs.html
- `sqlite3_vfs` interface: https://sqlite.org/c3ref/vfs.html

## Atomic commit, WAL, and sidecar pairing

SQLite's atomic-commit description makes durable outcome depend on filesystem
and storage assumptions around journals, synchronization, and deletion or
truncation. WAL mode adds a separate WAL and shared-memory protocol. A database
file copied, moved, restored, or deleted without the correct hot journal/WAL can
lose recovery evidence or expose an inconsistent snapshot.

- Atomic commit: https://www.sqlite.org/atomiccommit.html
- Write-ahead logging: https://sqlite.org/wal.html
- Temporary and journal files: https://sqlite.org/tempfiles.html
- Ways to corrupt a database: https://www.sqlite.org/howtocorrupt.html

## Bounded inference

The new test provides useful evidence because it executes the actual reset,
actual create-new publication, actual process exit, and actual SQLite reopen at
every application-visible publication frontier. It can detect disagreement
between durable database state, output namespace state, typed residue, and
recovery bytes.

It cannot infer what would happen if power failed between SQLite-internal writes
or if a storage device acknowledged synchronization dishonestly. The next model
should install a custom test VFS that records and selectively fails or crashes
on `xOpen`, `xWrite`, `xSync`, `xTruncate`, `xDelete`, and related operations,
then join those traces with the existing filesystem-publication state model.
Every generated trace should classify the result as old state, new state, or an
explicit recoverable/ambiguous state and compare that reference classification
with production C++.

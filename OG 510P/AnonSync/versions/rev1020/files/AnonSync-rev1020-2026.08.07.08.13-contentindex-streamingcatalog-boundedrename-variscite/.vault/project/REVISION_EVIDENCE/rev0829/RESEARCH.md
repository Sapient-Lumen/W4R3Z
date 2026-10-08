# Rev0829 research notes

The protocol owner is intentionally modeled as a recoverable cross-resource
state machine rather than as an atomic transaction. Primary SQLite documentation
supports that boundary.

## SQLite atomicity has a defined resource boundary

SQLite's atomic-commit protocol is about database transactions under documented
filesystem and storage assumptions. Rollback-journal mode uses journal creation,
flush, database writes, and journal deletion/truncation; WAL mode uses a distinct
WAL/shared-memory protocol. Neither mechanism includes an arbitrary JSON receipt
published by application code in another namespace.

- Atomic commit: https://sqlite.org/atomiccommit.html
- WAL: https://sqlite.org/wal.html
- Locking and hot-journal recovery: https://sqlite.org/lockingv3.html

The design consequence is fail-closed: prepare the exact receipt bytes and
filesystem capability before reset, but do not claim one commit across SQLite
and the receipt. After SQLite durability, a publication failure must carry the
known database outcome, exact expected receipt identity, namespace effect, temp
residue, and a narrowly authorized recovery action.

## Backup and file-copy semantics reinforce identity discipline

SQLite's online backup API copies a coherent live database through SQLite's own
connection-level mechanism. Raw file copying must account for journal/WAL
sidecars and locking. This supports AnonSync's rule that a path or successful
file operation is not sufficient authority: the owner must bind the live object
and the protocol-relevant sidecars.

- Online backup API: https://sqlite.org/backup.html
- WAL persistence and sidecars: https://sqlite.org/wal.html
- File locking: https://sqlite.org/lockingv3.html

## Testable fault scope

SQLite documents extensive use of alternative VFS implementations, simulated
I/O errors, crash processes, and recovery verification. Rev0829 executes the
real application protocol at selected reset/publication observations, but it
still enters SQLite through the ordinary VFS. The next oracle should record and
selectively fail or terminate at `xOpen`, `xWrite`, `xSync`, `xTruncate`,
`xDelete`, lock, shared-memory, and related calls, then compare reopened
application state with an independent reference model.

- SQLite testing: https://sqlite.org/testing.html
- PRAGMA behavior and durability controls: https://sqlite.org/pragma.html
- Security guidance for untrusted databases: https://sqlite.org/security.html

## C++ nested-exception lesson

The repaired defect is a general C++ API lesson: the presence of
`std::throw_with_nested` in source does not prove a nested cause exists. Its
conditional wrapper cannot derive from a `final` type. A durable-outcome error
must either inherit `std::nested_exception` itself and be constructed while an
exception is active, or remain non-final and be verified through runtime chain
traversal. Structural audits should assert the type relationship, but behavioral
tests must prove the actual cause survives.

## Bounded speculation

A future recovery record may be stronger as a content-addressed evidence node:
request digest, prior-state digest, new durable identity, publication effect,
residue identity, and process/owner generation become one signed or MAC-bound
node. That could later feed anti-entropy and deterministic convergence traces.
It must not become a bearer authorization token merely because it is hashed;
each consumer still needs owner, epoch, freshness, and policy checks.

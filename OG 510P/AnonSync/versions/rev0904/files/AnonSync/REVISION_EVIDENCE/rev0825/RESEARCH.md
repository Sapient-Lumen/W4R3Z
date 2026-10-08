# Rev0825 research notes

Rev0825 uses primary operating-system and SQLite documentation to constrain the
implementation, then treats those documents as hypotheses that still require
executable local proof.

## Atomic create-new publication

Linux `rename(2)` documents `RENAME_NOREPLACE` as refusing to overwrite
`newpath` and returning an error when that name already exists. It also notes
that support depends on the underlying filesystem. Rev0825 therefore uses the
typed `renameat2` interface relative to one pinned directory descriptor, tests
the actual runtime filesystem, preserves a competing inode and bytes, and fails
closed on unsupported POSIX platforms rather than building a racy emulation:
<https://man7.org/linux/man-pages/man2/rename.2.html>

The design inference is that preflight can only improve denial timing. It cannot
be publication authority because absence is not stable. The atomic no-replace
namespace operation is the linearization point for create-new evidence.

## SQLite commit and crash evidence

SQLite's atomic-commit documentation explains that correctness depends on the
filesystem and VFS assumptions around flushes, journal/WAL handling, and atomic
namespace operations. Its own crash testing varies failure points and damage,
then checks that transactions are wholly committed or rolled back and that the
database remains consistent:
<https://sqlite.org/atomiccommit.html>

SQLite's testing documentation describes I/O fault injection and separate
processes that simulate crashes, reorder or corrupt unsynchronized writes, and
run integrity checks, including compound failures. AnonSync's current
application cutpoint corpus is useful but is not equivalent to that VFS-level
coverage:
<https://sqlite.org/testing.html>

WAL documentation makes commit, checkpoint, and synchronization separate parts
of one persistent protocol and warns that the WAL is part of database state. It
also records a WAL-reset concurrency bug fixed in SQLite 3.51.3 and later. This
cube's hash-pinned SQLite 3.53.3 includes that upstream fix, but version
inclusion is not a substitute for AnonSync-specific protocol testing:
<https://sqlite.org/wal.html>

## Design consequences

A canonical reset receipt should be computed before the destructive transition
from stable authorization inputs. Attempt-local connection generation and later
state are useful diagnostics, but belong in observation reports, not event
identity.

The next oracle should combine a modified SQLite VFS with application
publication cutpoints. It should cover WAL writes and syncs, commit return and
postcommit observers, receipt temp reservation and writes, file sync,
`RENAME_NOREPLACE`, directory sync, process death, residual temp entries, and
compound failures. Recovery must derive classification from durable artifacts,
not from a return value that may have been lost with the process.

## Speculative next work

1. Build a deterministic cross-product of SQLite VFS fault points and receipt
   publication cutpoints, with a compact domain oracle for denied,
   committed/recoverable, and durably published states.
2. Consider a small append-only administrative event log or externally witnessed
   receipt digest when policy requires evidence to survive simultaneous loss of
   request, database, and local receipt directory.
3. Move hostile database interpretation into a disposable worker with CPU,
   address-space, wall-clock, descriptor, syscall, and filesystem ceilings.
4. Generalize canonical administrative event documents to retention,
   revocation, key-epoch migration, and other non-monotone transitions.
5. Resume the convergence algebra and classify replicated operations by
   commutativity, idempotence, monotonicity, causal dependencies, and epoch
   compatibility before selecting CRDT or coordination mechanisms.

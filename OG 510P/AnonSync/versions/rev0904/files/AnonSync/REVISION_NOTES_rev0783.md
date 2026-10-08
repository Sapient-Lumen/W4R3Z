# AnonSync rev0783 — process-bound SQLite ownership and lineage recovery

## Mission

AnonSync is an **evidence-authorized convergence engine**. Transport receipt,
callback success, a worker label, a database pointer, and a successful syscall
are observations, not authority. Authority must bind the exact generation that
performs an operation and must be checked by the operation that consumes it.
Durable convergence authority is reconstructed from content-bound evidence;
live C++ capabilities are narrower process/thread/lifetime proofs and must
never be mistaken for durable truth.

Rev0783 applies that rule to SQLite ownership after `fork()`. SQLite explicitly
forbids carrying an open database connection across a fork. A child inherits
pointer-shaped bytes, C++ destructors, thread-local bytes, and file descriptors,
but none of those copies authorizes use or cleanup of the parent's SQLite
objects.

## Lineage recovery

The declared preceding artifact, rev0782, is not a source handoff. It contains
50 files but no C++, headers, tests, CMake project, or README, and its own
required release gate is false. Rev0783 therefore fails closed on the label and
reconstructs from the last verified full-source archive, rev0778. The exact
archive hashes, rejection report, and reconstruction statement are under
`REVISION_EVIDENCE/rev0783/`.

Concepts described in the source-less intermediate evidence are not accepted as
implemented merely because they were named. The direct `_Exit` fail-stop and
process-bound owner behavior were independently reimplemented and retested in
this source tree.

## Correctness changes

### Process-bound owner slots

`sync_sqlite_process_incarnation` defines one nonserializable live process
identity and one stable capability-violation exit status. A mismatch exits with
`std::_Exit(86)`, bypassing replaceable terminate handlers, atexit hooks, and
C++ unwinding.

`sync_sqlite_handle_slot` is the shared owner for `sqlite3*` and
`sqlite3_stmt*`. Every read, reset, move, output acquisition, output adoption,
and destructor validates the minting process before touching SQLite. The
connection policy uses `sqlite3_close_v2()` and the statement policy uses
`sqlite3_finalize()`.

SQLite output parameters are handled by a nonmovable scoped guard. It adopts a
non-null output even when the SQLite call returns an error, preventing an
error-path leak. Two simultaneous output guards are rejected. Public raw
adopt/release operations are intentionally absent so a cached parent pointer
cannot be relabeled as a child-local owner.

### Authority-bearing objects

Connection proofs, retained leases, transaction boundary proofs, typed
transactions, SQLite client-data sentinels, and payload-schema rollback guards
now carry process identity. Child-side observation returns false where that is
safe; child-side move, finalization, or cleanup fails stopped before SQLite.
Thread incarnations are reseeded after fork because thread-local bytes are
copied into the child.

The old mutex-capability failure path used `std::terminate()`, allowing a hostile
or accidental terminate handler to reinterpret the violation. It now shares
the unhookable `_Exit(86)` primitive. Tests deliberately install a hostile
terminate handler with a different exit status.

### Replay-ledger and lock ownership

The long-lived SQLite/WAL replay-ledger connection and its internal prepared
statement owner now use the common process-bound slots. The peer-ingestion
translation unit's duplicate private connection/statement owner pair was
removed in favor of the shared boundary.

Restore locks and write-gate locks are process stamped. Their inherited
destructors fail stopped before closing descriptors. The write-gate recursion
set is thread-local and was previously copied across fork; a child could see the
parent's path and incorrectly skip acquiring a lock as “nested.” The set now
carries process identity and discards inherited recursion evidence before a
child-local acquisition.

## Executable evidence

A fresh GCC Debug build completed after one recorded execution-window
interruption and passed **41/41 CTest tests**. The entire suite repeated three
times without failure. Focused direct results are:

- domain model: **588 passed, 0 failed**;
- peer-ingress lifecycle: **49 passed, 0 failed**;
- SQLite support: **61 passed, 0 failed**;
- connection authority: **98 checks, 0 failures**;
- process/fork authority: **35 checks, 0 failures**;
- restore/write-gate: **9 passed, 0 failed**.

The process/fork executable passed 100 consecutive runs, totaling **3,500/3,500
checks**. Focused GCC Release, GCC ASan/UBSan, and Clang lanes each passed the
support, connection-authority, and process-authority tests.

The full optimized build was attempted and recorded, but the 24,000-line
`sync_domain.cpp` optimization exceeded the cloudtainer execution ceiling. It
is an optional build-scalability limitation, not represented as a passing full
Release lane. The changed focused Release boundary rebuilt and passed.

## Audit result and deliberate limits

The process-authority audit passes **52/52 checks**, the updated mutex audit
passes **64/64**, the transaction-stack audit **45/45**, and the payload
transaction audit **38/38**. The lexical inventory retains 332 raw SQLite
pointer declarations for review rather than pretending that every raw pointer
is an owner defect.

The most important unresolved seam is public borrowed-handle authority. Several
APIs still accept `sqlite3*`; a raw pointer cached before fork can bypass the
owner slot where no independent process-bound proof is consumed first. The next
boundary should be a typed non-owning capability carrying `{pointer,
process_id}` and should migrate transaction construction, schema attestation,
and other public raw-handle entry points.

Rev0783 does not claim arbitrary work is safe after a multithreaded `fork()`.
POSIX restricts the child to async-signal-safe operations until `exec()`. The
child-local reopen tests model a controlled single-threaded fork path; the usual
fork-and-exec child should execute or `_Exit` without running AnonSync teardown.
No `pthread_atfork` choreography can make an inherited SQLite connection valid.

Process IDs and thread incarnations are live-memory fences, not serialized or
restart authority. Power-loss durability still needs a fault-injecting VFS and
an executable transition oracle across WAL write, sync, checkpoint, rename,
directory-sync, and receipt boundaries.

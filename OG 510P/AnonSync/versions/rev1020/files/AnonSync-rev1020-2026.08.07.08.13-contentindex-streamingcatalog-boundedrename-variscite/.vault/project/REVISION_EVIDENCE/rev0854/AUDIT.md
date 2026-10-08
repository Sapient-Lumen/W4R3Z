# Rev0854 deep audit

## Finding

The busy-handler, progress-handler, and authorizer lifetime owners each used a
named `sqlite3_set_clientdata()` claim together with a singleton callback
setter. SQLite serialized each individual API call on a `FULLMUTEX` connection,
but the logical transition was still split across multiple calls:

1. observe the named claim slot as empty;
2. publish a pending lifetime sentinel; and
3. install the retained callback.

Two legitimate constructors could interleave those steps. Both could observe an
empty slot; the later client-data publication would then replace and
synchronously destroy the first pending or live sentinel. The fail-stop cleanup
correctly diagnosed unauthorized replacement, but ordinary duplicate attachment
became process termination rather than one winner and one recoverable rejection.

This was a severe authority-composition defect. Rev0853 protected the busy slot
against `sqlite3_busy_timeout()`, but owner-versus-owner attachment remained
non-atomic in all three retained callback protocols.

## Correction reviewed

`SyncSqliteDatabaseMutexGuard` now owns one exact recursive
`sqlite3_db_mutex()` entry. It is noncopyable and nonmovable, binds its own
lifetime to the current process and exact C++ thread incarnation, and rejects a
null mutex in the authority-bearing lane. One explicitly named
`PermitUnserialized` mode exists only for the reviewed single-user `NOMUTEX`
busy-timeout compatibility path and cannot authorize client-data claims.

The client-data claim API now requires the exact live guard in the C++ type
surface for `attach`, `require_live`, and `detach`. A wrong-database, released,
or nonauthorizing guard is rejected. Each retained callback owner holds one
guard across the complete claim-plus-setter transition and across liveness
proof, callback revocation, and claim destruction. Exact connection-generation
borrows remain live until after the SQLite-owned mutex is left.

The refactor also removes two divergent local scoped-mutex implementations. The
shared owner is now the only scoped SQLite database-mutex guard; connection
authority retains a separately reviewed manual enter/leave pair for its longer-
lived typed lease.

## Runtime proofs

The focused runtime corpus contains **455 checks**:

- busy-handler owner: **40/40**;
- verification budget: **110/110**;
- authorizer owner: **22/22**;
- shared SQLite support and mutex guard: **86/86**;
- connection authority: **153/153**; and
- inherited-process authority: **44/44**.

Each singleton callback owner includes a 64-iteration simultaneous-construction
oracle. Two contenders begin together against one exact serialized connection;
exactly one succeeds, exactly one receives the expected ordinary rejection, the
winner remains callable, teardown removes the exact claim, and no generation
borrow leaks. The repeatability lane ran the four affected executables 100 times
each: **400/400 process runs** and **19,200 duplicate-owner races**.

Direct guard tests cover null and empty-label rejection, exact mutex identity,
recursive entry, cross-thread exclusion, one-way transfer, strict `NOMUTEX`
rejection, and the explicit nonauthorizing compatibility lane.

## Audit/refactor composition

Focused structural checks are **311/311**:

- SQLite mutex capability: **77/77**;
- busy-handler owner: **38/38**;
- verification budget: **63/63**;
- authorizer owner: **42/42**; and
- SQLite process authority: **91/91**.

All **43/43** registered structural audits pass. One authorizer audit was
refactored from an exact single-line spelling assertion to a whitespace-tolerant
semantic expression check. This preserves the null-input invariant while
removing format-only failure coupling.

The release verifier requires the guard, direct runtime tests, and composed
audits beginning with rev0854, while the same verifier still accepts the sealed
rev0853 parent at 26/26 ZIP and 22/22 directory checks.

## Residual risk

This is source-confined composition, not universal SQLite interposition. Foreign
code holding a raw `sqlite3*` can still call alternate callback setters, replace
a known client-data name, or close/use the handle outside the typed protocol.
The guard proves the execution and lifetime of its own mutex entry; inherited
raw-handle rejection remains the responsibility of the exact-generation owner
used before guard construction.

Repeated adversarial scheduling is not ThreadSanitizer. Arbitrary concurrent
C++ object teardown, full-project sanitizers, Release all-target behavior,
Windows runtime behavior, distributed convergence, confidentiality, anonymity,
metadata hiding, key recovery, hostile-worker isolation, and secure erasure are
not claimed.

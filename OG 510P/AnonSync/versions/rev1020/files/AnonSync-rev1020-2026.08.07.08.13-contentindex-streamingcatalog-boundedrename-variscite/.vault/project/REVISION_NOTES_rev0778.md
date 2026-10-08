# AnonSync rev0778 — exact thread-incarnation and close-lifetime mutex fencing

## Heart of the mission

AnonSync is an evidence-authorized convergence engine. A callback, pointer,
worker, successful write, or transport receipt is an observation; none is
sufficient authority. Authority must bind the exact dynamic generation that
performs an operation, be checked at consumption, and fail closed when the
proof can no longer be reconstructed.

Rev0778 applies that rule to the lowest live SQLite boundary. A retained
`sqlite3_db_mutex()` entry is not merely “a serialized connection.” It is one
exact recursive entry owned by one C++ thread lifetime and valid only while one
exact SQLite connection lifetime remains open.

## Severe faults corrected

### Foreign-thread release

Rev0774 retained the connection mutex across a typed transaction, but thread
affinity was documentation only. SQLite specifies that `sqlite3_mutex_leave()`
must be called by the same thread that entered the mutex and that foreign leave
is undefined behavior. A copied authority query could also block behind the
recursive entry held by its own live owner.

Rev0778 assigns a monotonic process-local incarnation to each C++ thread
lifetime. Every retaining lease and transaction boundary captures it. Foreign
observation returns false before SQLite access, explicit foreign COMMIT or
ROLLBACK throws without revoking the owner, and foreign move/destruction fails
stopped before touching SQLite-owned state.

### Same-thread close invalidation

A more severe lifetime seam was found during the audit. Because the connection
mutex is recursive, the owner thread could call `sqlite3_close_v2()` while its
lease still retained an outer entry. Bundled SQLite 3.53.3 invokes connection
client-data destructors, marks the connection zombie, leaves the inner entry,
and can free the mutex while the outer AnonSync entry still exists. The later
lease destructor would then call `sqlite3_mutex_leave()` through a dangling
pointer.

Rev0778 installs a second, versioned SQLite client-data sentinel. Each retained
mutex entry increments its count while the connection mutex is held and
consumes its own pointer before release. Closing or replacing the sentinel with
a nonzero count terminates immediately. This count is deliberately only a
close-lifetime pin, not a transaction or authorization generation.

## Refactor

`src/sync_sqlite_mutex_capability.{hpp,cpp}` now owns:

- monotonic thread-incarnation allocation without `std::thread::id` reuse;
- exact thread comparison and deterministic foreign-thread rejection;
- the SQLite-owned retained-mutex lifetime sentinel;
- overflow, underflow, corruption, replacement, and close-order fail-stop; and
- one shared lease-shape validator used by construction, destruction, and move.

The authorizer bridge still owns every direct production
`sqlite3_mutex_enter()`/`sqlite3_mutex_leave()` call. The split is by invariant,
not line count: thread and connection lifetime are isolated from policy,
authorizer generations, and transaction SQL.

## Executable proof

The connection-authority executable now reports **98 checks, 0 failures**. It
covers owner and foreign observation, non-revoking foreign authority checks,
foreign COMMIT/ROLLBACK latency, owner recovery, owner-thread move construction,
self-move and move assignment, foreign move/destruction fail-stop, live-lease
close, live fenced- and unfenced-transaction close, sentinel replacement,
`sqlite3_close_v2()` zombie close,
foreign close serialization, normal post-release close, and NOMUTEX rejection.

The fail-stop scenarios run in child processes with a dedicated terminate exit
code. The test has a finite 15-second CTest timeout. One hundred consecutive
executions passed, totaling **9,800/9,800 checks**.

`tools/audit_sqlite_mutex_capability.py` passes **63/63 source-shape checks** and
inventories all nine direct production mutex calls and both reviewed client-data
owners. The existing transaction-stack audit passes 45 checks, the payload
authority audit passes 38, and the updated authorizer ownership audit passes.

## Repository hygiene correction

The source cube contained **488 tracked build artifacts totaling 286,095,753
bytes** under `build-baseline/` and `build-rev0778-baseline/`. These included
host-specific binaries, object files, compiler probes, CMake caches, and stale
test logs. They were neither portable evidence nor source and could make a
reviewer execute obsolete code accidentally.

Rev0778 deletes those tracked products and adds a root `.gitignore` for build,
Python cache, and crash artifacts. Validation remains in small text and JSON
records under `REVISION_EVIDENCE/`; reproducible binaries are rebuilt from
source.

## Validation

- fresh GCC 14.2 Debug build completed after one transparently recorded tool
  timeout and resume;
- full Debug CTest: **40/40 passed**;
- full Debug CTest repeated three times: **120/120 passed**;
- direct domain model: **588/0**;
- direct peer-ingress lifecycle: **49/0**;
- SQLite support: **61/0**;
- schema attestation: **58/0**;
- connection authority: **98/0**, repeated 100 times;
- GCC Release focused tests: **2/2 passed**;
- GCC ASan/UBSan focused tests: **2/2 passed**;
- Clang 17 focused tests: **2/2 passed**.

GCC Release reports one optimizer warning in the unchanged bundled SQLite
amalgamation. No warning was emitted from changed AnonSync source. The warning
is retained in the evidence rather than suppressed.

## Deliberate limits and next work

The sentinel converts invalid close order into fail-stop; it does not make a raw
`sqlite3*` generally lifetime-safe. A connection actor/strand should eventually
own open, operation dispatch, transaction finalization, and close so live SQLite
capabilities never cross execution contexts.

Fork remains unproved. Thread-local and process memory are copied into a child,
so inherited connection proofs need a process epoch or an explicit prohibition
on post-fork reuse. Process-crash tests also remain weaker than power-loss
proof. A fault-injecting VFS should enumerate WAL write, sync, checkpoint,
truncate, directory, and reset boundaries against an executable transition
oracle.

The transaction-stack audit still inventories 95 legacy raw controls outside
peer-ingress production. `src/sync_domain.cpp` remains 24,523 lines. Both should
be reduced by invariant-owned repository/state-machine slices rather than
mechanical file splitting.

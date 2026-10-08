# Rev0778 research — SQLite mutex ownership and close lifetime

Research was limited to upstream SQLite documentation, the bundled SQLite
3.53.3 amalgamation, and the current C++ working draft.

## Primary references

- SQLite mutex API: https://sqlite.org/c3ref/mutex_alloc.html
- SQLite database-connection mutex: https://sqlite.org/c3ref/db_mutex.html
- SQLite threading modes: https://sqlite.org/threadsafe.html
- SQLite close semantics: https://sqlite.org/c3ref/close.html
- SQLite database connection client data:
  https://sqlite.org/c3ref/get_clientdata.html
- C++ `thread::id`: https://eel.is/c++draft/thread.thread.id
- Bundled source: `third_party/sqlite-3.53.3/sqlite3.c`, especially
  `sqlite3Close()` and `sqlite3LeaveMutexAndCloseZombie()` around lines
  188628–188848.

Accessed 2026-07-14.

## Conclusions

### Serialized calls are not transferable mutex ownership

SQLite serialized mode allows API calls concerning one connection to be made
from multiple threads by serializing them. The lower-level mutex contract is
more specific: `sqlite3_mutex_leave()` exits a mutex entered by the same thread,
and behavior is undefined when the caller does not own the entry or the mutex
is no longer allocated.

AnonSync intentionally holds one recursive entry across a whole typed
transaction. That creates a thread-affine dynamic capability even though the
underlying connection normally permits serialized calls from many threads.

### `std::thread::id` is not an incarnation

The C++ standard permits a `thread::id` value to be reused after a terminated
thread can no longer be joined. Hashing it preserves reuse and adds collision
risk. Rev0778 therefore allocates a process-local monotonic incarnation on each
thread's first use. It is nonsecret and nonserializable; its purpose is stale
capability rejection, not authentication.

### Client data gives a close callback, not automatic ownership extension

`sqlite3_set_clientdata()` attaches a named pointer and destructor to a
connection. SQLite invokes that destructor on replacement, allocation failure,
or connection close. Destructor ordering among names is unspecified.

Rev0778 uses this mechanism only as a tripwire. The shared counter does not keep
SQLite alive by reference counting. Instead, any close or same-name client-data
replacement that reaches the destructor while a retained mutex entry exists
terminates before invalid state can return to its owner. Executable child-process
checks cover live leases, both fenced and unfenced typed transactions, explicit
sentinel replacement, and deferred zombie-close destruction.

### The bundled close path explains the dangling-pointer seam

SQLite 3.53.3 enters the recursive connection mutex inside `sqlite3Close()`,
destroys client data, marks the connection zombie, and delegates to
`sqlite3LeaveMutexAndCloseZombie()`. When no dependent objects remain, that
function leaves and frees the mutex. An outer recursive entry retained by the
caller is not a SQLite-tracked dependent object.

For `sqlite3_close_v2()` with an outstanding statement, the connection becomes
a zombie and final physical deallocation is deferred, but client-data
destructors are still invoked during the close call. The rev0778 zombie-close
death test covers this path.

## Design implications

1. **Connection actor/strand.** One execution context should own every
   `sqlite3*`, typed transaction, and close. Other threads submit immutable
   commands and receive canonical outcomes. Thread incarnation then becomes a
   defense-in-depth assertion rather than a cleanup policy.
2. **Close as an owned transition.** A future wrapper should make close consume
   the connection owner only after all statements, backups, blobs, leases, and
   transactions are absent. External raw close cannot then bypass C++ lifetime.
3. **Process epoch after fork.** A forked child inherits addresses, atomics,
   thread-local values, and possibly inconsistent native mutex state. Bind live
   capabilities to a process epoch changed by an at-fork child hook, or prohibit
   inherited SQLite use entirely. Upstream fork constraints must be researched
   before implementation.
4. **Fault-injecting VFS oracle.** Thread and close lifetime do not prove
   durability. Inject failures at WAL write, sync, checkpoint, truncate,
   directory sync, and reset boundaries; compare restart state with an
   executable transition oracle.
5. **Privacy-preserving telemetry.** Count invariant classes and call-site
   identifiers, not OS thread IDs, exact timestamps, database paths, or stable
   peer identifiers. The incarnation should never leave the process.

## Uncertainty

The close tripwire relies only on public client-data destruction semantics for
correct fail-stop behavior, but line-level ordering observations are specific to
the bundled SQLite 3.53.3 source. A future SQLite update should rerun both the
source audit and death tests rather than assuming identical internal order.

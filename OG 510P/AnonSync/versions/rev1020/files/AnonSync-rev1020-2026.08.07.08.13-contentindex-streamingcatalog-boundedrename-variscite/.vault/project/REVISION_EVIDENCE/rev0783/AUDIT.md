# rev0783 deep audit — process authority, ownership, and handoff truth

## Heart of the mission

AnonSync's security model is not “the code that ran most recently wins.” It is
**evidence-authorized convergence**: every transition must consume exact,
content-bound, generation-bound evidence. Live SQLite handles participate only
as narrow capabilities. Pointer identity, successful open, mutex serialization,
thread-local state, and inherited file descriptors do not authorize another
process to use or clean up an object.

## Severe findings corrected

1. **Raw owner inheritance.** Common connection and statement RAII wrappers
   stored raw pointers, so child destruction could invoke SQLite on parent-owned
   objects. Process-bound slots now fence access, move, reset, output adoption,
   and destruction.
2. **Output-parameter ambiguity.** SQLite may return a non-null connection on an
   error. A scoped output guard now owns that result before exception paths can
   leak it and rejects concurrent output guards.
3. **Duplicate owner semantics.** Peer ingestion maintained a private owner
   pair, and the replay ledger retained a long-lived raw connection plus raw
   statement wrapper. They now use the shared invariant-owned boundary.
4. **Authority copies after fork.** Proofs, leases, transaction generations,
   client-data sentinels, payload rollback guards, and thread incarnations now
   include process evidence or reseed in the child.
5. **Hookable fail-stop.** Mutex lifetime faults called `std::terminate()`. A
   replaceable handler could change the outcome. They now call direct
   `_Exit(86)`; adversarial tests install a hostile handler with another code.
6. **Copied recursion state.** The write-gate's thread-local path set survived
   fork and could classify a child acquisition as nested, skipping the lock.
   The set now carries process identity and clears inherited evidence.
7. **Inherited file-lock destruction.** Restore/write-gate objects could close
   inherited descriptors and mutate recursion bookkeeping. Destructors now
   fail stopped before either action.
8. **False parent artifact.** Rev0782 passed ZIP syntax but omitted the project
   and had a failed gate. A new verifier rejects source-less or partial release
   cubes and exact-manifest mismatches.

## Refactor boundary

The new split is by invariant:

- `sync_sqlite_process_incarnation`: live process identity and direct fail-stop;
- `sync_sqlite_handle_slot`: exact owning connection/statement lifecycle and
  output acquisition;
- `sync_sqlite_mutex_capability`: exact thread entry and connection-close
  lifetime;
- `sync_sqlite_connection_authority`: authorizer generation and serialized
  use-time proof;
- `sync_sqlite_transaction`: exact transaction generation;
- replay-ledger file locks: kernel lock ownership and recursion evidence.

This is preferable to another local RAII class in each large translation unit.
One owner abstraction can now be audited and tested once.

## Static audit

`tools/audit_sqlite_process_authority.py` passes 52 checks and records all raw
SQLite pointer candidates. It deliberately reports four residual risks instead
of declaring universal coverage. The updated mutex-capability audit passes 64
checks; authorizer ownership has no violation; transaction stack passes 45;
payload transaction authority passes 38.

## Remaining high-risk seam

The new slot protects owners, not every borrowed pointer. Public constructors
and functions still accept `sqlite3*`. A parent pointer cached outside the slot
can be passed to a child API that stamps the *current* process unless that API
first consumes a process-bound proof. This is the highest-priority next fix.

A `SyncSqliteBorrowedConnection` capability should contain the pointer and
minting process identity, expose checked `get()`, be constructible only from a
process-bound owner/proof, and replace raw public transaction/schema entry
points. Compatibility raw paths should be isolated, named unsafe, and removed
from production call sites rather than silently stamping current PID.

## Other limits and waste

- Stack-scoped raw SQLite helpers remain in replay/reporting/test code. They are
  not long-lived fields, but rev0783 does not make a mid-call fork safe.
- `pthread_atfork` cannot make inherited SQLite handles valid and can add lock
  ordering deadlocks; no such workaround is claimed.
- PID/thread values are live-process evidence only, never durable or serialized.
- Process-kill tests do not prove power-loss ordering.
- The oversized domain and reporting translation units make clean optimized
  builds exceed cloudtainer windows. Modularization is now a build reliability
  and reviewability requirement, not cosmetic cleanup.

## Recommended next sequence

1. Introduce and migrate the typed borrowed SQLite connection capability.
2. Move open/dispatch/transaction/close into one connection actor or strand.
3. Extract checkpoint and peer-ingress repositories from `sync_domain.cpp`
   around durable aggregate ownership.
4. Add a fault-injecting SQLite VFS and executable crash-state oracle.
5. Add a canonical durable spool only after its envelope and transaction-order
   contract are fixed and versioned.

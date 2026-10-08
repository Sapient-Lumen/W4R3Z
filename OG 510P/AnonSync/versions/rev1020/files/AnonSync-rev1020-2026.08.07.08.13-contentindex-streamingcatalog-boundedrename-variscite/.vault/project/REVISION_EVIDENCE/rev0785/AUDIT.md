# rev0785 deep audit — exact owner-generation SQLite lifetime authority

## Heart of the mission

AnonSync is not a byte copier. It is an evidence-authorized convergence engine.
The central engineering question is always: **what exact evidence authorizes
this transition after interruption, reuse, concurrency, or adversarial input?**
At the SQLite boundary, a raw `sqlite3*` answers only where an object happened
to reside. It does not prove which owner generation minted it, whether that
owner remains live, whether a statement still depends on it, whether the
transaction guard still owns the boundary, or whether the process inherited it
through `fork()`.

## Severe direction rejected

An incomplete predecessor attempt introduced a standalone owner-generation
class using `std::shared_ptr` plus `std::mutex` and a child-side quarantine
method that locked the copied mutex after `fork()`. If another parent thread
held that mutex at fork, the child could block forever. The class was also not
integrated into the existing SQLite ownership boundary, creating two competing
truths while most call sites continued using the old slot.

Rev0785 does not package that direction. It integrates generation and borrowing
into the existing `ProcessBoundHandleSlot`, uses immutable process provenance,
and checks that provenance before entering a lock-free lifecycle guard. The
child never attempts to repair or close inherited SQLite state; misuse exits
immediately without unwinding.

## Implemented invariants

1. Every materialized owner-state allocation is bound to its creating process,
   even while empty or after a null SQLite output.
2. Every successful non-null output advances a monotonic nonzero generation.
3. A borrow binds `{shared state, exact handle, process, generation}` and keeps
   the owner generation alive across owner moves.
4. Reset/destruction refuses any active borrow.
5. Output acquisition is exclusive, process-bound, and valid only for an empty,
   unborrowed owner.
6. Lifecycle serialization uses an always-lock-free PID atomic and a strong
   compare-exchange. Weak-CAS spurious failure cannot become a false foreign
   owner verdict.
7. Managed connection close rejects an open transaction and rejects
   `SQLITE_BUSY`; it never silently creates a zombie connection.
8. Typed statements privately retain the database-generation borrow until the
   private statement owner has finalized.
9. The public statement surface is a read-only view, not a movable owner slot.
10. Typed transactions retain the owner generation through the live boundary
    and release it only after transaction and mutex authority are revoked.
11. Fork-copied owners, borrows, output guards, statements, transactions, and
    destructors fail stopped before touching SQLite or inherited bookkeeping.
12. Critical peer-ingestion sidecar transaction boundaries use the typed guard.

## Refactor/audit findings

The peer-ingestion unit had a second mini SQLite support layer with weaker error
normalization and duplicate reset/bind/column code. It now delegates to the
common checked implementation. This removes maintenance divergence and makes
owner-generation migration visible in one support layer.

The public statement wrapper originally exposed the movable owner slot even
after adding a private database pin. A caller could move `statement.stmt` out,
destroy the wrapper (releasing the pin), and keep stepping the detached
statement. The final design replaces that field with a nonmovable `HandleView`;
compile-time tests reject `out()`, `reset()`, and ownership movement through the
view.

The lifecycle spin guard originally used `compare_exchange_weak`. A spurious
failure can leave the observed value equal to zero; code interpreting every
failure as an extant owner could fail-stop healthy contention. The guard now
uses strong CAS, and both a lexical release audit and a six-thread/24,000-borrow
regression protect this detail.

## What remains missing

The exact-generation boundary is not yet universal. The owner audit records:

- 17 raw prepare sites;
- 70 raw transaction-control sites;
- three legacy `sqlite3_close_v2()` sites.

The most important remaining flaw is raw-pointer laundering through compatibility
overloads. The slot can prove lifetime only when callers retain a borrow. A raw
pointer cached outside the borrow can race close or cross process boundaries
without that proof. Migration should proceed module-by-module, deleting raw
overloads only after each invariant owner has converted.

`SQLITE_OPEN_FULLMUTEX` is currently a runtime/open-site property rather than a
type property. Cross-thread borrow-accounting is safe, but cross-thread SQLite
use is safe only for a serialized connection. A future borrowed-connection type
should carry and verify the exact mutex-mode/open-profile evidence.

The codebase still pays heavily for historical concentration: `sync_domain.cpp`
is 24,528 lines and `sqlite_replay_ledger.cpp` is 4,466 lines. Their size slows
fresh compiler lanes and makes ownership review harder. Decomposition should
follow durable aggregates and authority transitions, not arbitrary helper
categories.

Finally, process-kill tests do not prove power-loss ordering. A fault-injecting
SQLite VFS and executable state oracle are still required to explore crash cuts
around WAL writes, syncs, checkpoints, spool rename, directory sync, database
receipt, and acknowledgement.

## Speculative next architecture

A useful end state is a small capability lattice:

- `DbOwnerGeneration`: unique close authority plus monotonic generation;
- `DbBorrow<Serialized>`: exact-generation use authority with proven mutex mode;
- `TransactionGeneration`: one typed begin/end boundary and retained mutex;
- `StatementGeneration`: exact statement plus owning DB borrow;
- `DurableReceipt`: content/generation-bound evidence reconstructed after crash.

No conversion from a raw address should mint one of these capabilities. A raw
address may be extracted transiently only while an existing capability remains
live. This would make lifetime authority compositional and allow the compiler
and release audits to reject most stale-pointer paths before runtime.

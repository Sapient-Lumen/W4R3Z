# AnonSync rev0785 — exact owner-generation SQLite lifetime authority

## Mission

AnonSync remains an **evidence-authorized convergence engine**. A transport
receipt, callback, worker label, raw address, successful syscall, or in-memory
object is an observation. It becomes authority only when the operation that
consumes it verifies the exact content, generation, process, thread, and
lifetime evidence appropriate to that boundary. Durable convergence authority
must remain reconstructible after a crash; these C++ capabilities are narrower
live-process fences and are never serialized.

## Correctness work

Rev0785 integrates an exact owner-generation borrow into the existing
process-bound SQLite owner slot instead of shipping a second competing owner
abstraction. Each materialized owner state carries immutable process provenance,
a monotonic nonzero generation, exact borrow accounting, and a process-bound
output reservation. Owner moves preserve the same generation state. Reset,
reopen, statement preparation, transaction construction, and destruction all
fail closed when their exact lifetime preconditions are not met.

The lifecycle lock is a lock-free atomic protocol rather than an inherited
`std::mutex`. A child process fails stopped before touching copied SQLite or
shared-owner state. The implementation deliberately uses a strong
compare-exchange: treating a spurious weak-CAS failure as foreign ownership
would randomly terminate a correct process under contention.

Managed connection destruction now rejects open transactions and uses strict
`sqlite3_close()`. An unfinalized statement therefore produces a fatal lifetime
ordering defect instead of being hidden behind `sqlite3_close_v2()` zombie
semantics. Typed statements retain the exact database generation until finalization;
typed transactions retain it through begin and release it only after commit or
rollback and retained-mutex revocation.

A second review closed a laundering path in the statement wrapper. Its public
`stmt` member is now a non-owning, nonmovable `HandleView`; the actual statement
owner slot and database-generation pin are private and destruct in the required
order. Call sites retain the familiar SQLite C API spelling without being able
to move, reset, or refill statement ownership independently.

## Refactor

Peer-ingestion duplicate bind/column/exec helpers now delegate to the common
checked SQLite support layer. Sidecar transaction-control paths were migrated
from raw SQL boundaries to `SyncSqliteTransaction`, and selected domain and
peer-ingestion prepares now consume the typed owner slot. The default sanitizer
lane instruments AnonSync C++ without recompiling the multi-megabyte pinned
SQLite amalgamation; a dedicated opt-in preserves upstream-boundary coverage.

## Validation

The exact final implementation projection passes:

- fresh GCC Debug build and **42/42 CTest tests**;
- owner-generation/fork/race suite, **10/10 consecutive repetitions**;
- GCC ASan/UBSan focused authority lane, **5/5**;
- GCC Release focused authority lane, **5/5**;
- Clang Debug with `-Werror`, **5/5**;
- owner-generation source audit, **14/14 required invariants**;
- process authority, **56/56**; mutex capability, **64/64**;
- transaction-stack authority, **45/45**; payload authority, **38/38**;
- SQLite authorizer ownership, **0 violations**.

The Release build log preserves one cloud command-window interruption before a
successful resume. It is not represented as a compiler failure.

## Deliberate limits and next work

Raw `sqlite3*` compatibility APIs remain. The audit inventories 17 raw prepare
sites, 70 raw transaction-control sites, and three `sqlite3_close_v2()` calls in
the legacy replay-ledger subsystem. These are explicit staged-migration debt,
not claims of complete conversion. A cached raw pointer can still bypass the
new owner pin where a caller chooses a compatibility overload.

The next correctness boundary should encode connection mutex mode in the
borrowed capability and remove raw transaction/schema entry points module by
module. After that, split the 24,528-line domain unit and 4,466-line legacy
replay-ledger unit around invariant-owned aggregates, then add a fault-injecting
VFS/state oracle for WAL write, sync, checkpoint, rename, directory-sync, and
receipt ordering.

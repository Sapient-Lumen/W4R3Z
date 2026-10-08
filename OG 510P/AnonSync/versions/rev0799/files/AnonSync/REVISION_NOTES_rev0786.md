# AnonSync rev0786 — observed serialized-generation SQLite authority

## Mission

AnonSync remains an **evidence-authorized convergence engine**. Transport,
callbacks, pointer values, open flags, and successful SQLite calls are
observations. They are not authority by themselves. Every transition should be
accepted only through evidence bound to the exact content, process,
connection generation, transaction, and durable receipt appropriate to that
boundary. The connection capabilities added here are live-process safety
proofs; they are intentionally non-serializable and do not replace durable
crash-recovery evidence.

## Severe boundary defect closed

Rev0785 pinned statements and transactions to an exact database-owner
generation, but that generation did not prove the connection's actual SQLite
mutex mode. A slot could adopt a connection opened with `SQLITE_OPEN_NOMUTEX`,
and typed helpers would still treat the borrow as sufficient authority. Open
flags at another call site express intent; they do not constitute evidence
carried by the adopted owner generation.

Rev0786 captures the result of `sqlite3_db_mutex()` exactly once when a database
output is adopted. The process-bound owner freezes `{handle, process,
generation, mutex mode, mutex identity}` as one tuple. A missing per-connection
mutex is classified as `Unserialized`; a present mutex is classified as
`Serialized`. Moves preserve the evidence, reset destroys it, and reopen
creates a fresh generation with fresh evidence.

Evidence validation after adoption is deliberately SQLite-free. Threading mode
is immutable for one open connection, while re-reading SQLite state during a
generic borrow operation could itself become concurrent SQLite API use on a
`NOMUTEX` handle. The owner therefore captures once at the publication boundary
and thereafter compares only the frozen exact-generation tuple.

## Capability and refactor

`SyncSqliteSerializedDbBorrow` is move-only, cannot be constructed from a raw
`sqlite3*` or generic borrow, and has no implicit raw-pointer conversion. Its
single mint first acquires an exact owner-generation borrow, then rejects any
mode other than `Serialized` before SQL or an authorizer callback can run.
Typed exec, prepare, schema probes, counts, statements, and transactions now
mint and retain this stricter authority.

Peer-ingress read and write connections no longer maintain a second cached raw
`sqlite3*` truth beside the owner slot. Each connection retains one serialized
borrow for its lifetime; statements and transactions retain their own exact
borrow generations. The write-transaction helper now accepts the owner slot,
and retention paths derive a transient raw address explicitly from a live
serialized capability only at the immediate C API boundary.

Fork ordering remains fail-closed: inherited process provenance is rejected
before copied generation state or SQLite is consulted. Destruction order keeps
statement and connection capabilities ahead of the unique owner so strict
close cannot be laundered through a cached address.

## Adversarial coverage

The owner-generation suite now verifies both `FULLMUTEX` and `NOMUTEX`
classification, preservation across owner moves, fresh evidence on reopen,
strict-capability non-forgeability, rejection before SQL/authorizer activity,
no leaked pin or transaction, typed statement projection, cross-thread use of a
serialized capability, contended bookkeeping for an unserialized generic
borrow, and fail-stop behavior for an inherited serialized borrow after
`fork()`. The direct suite reports **258 checks**.

The final implementation projection passes:

- fresh GCC Debug build and **42/42 CTest tests**;
- owner-generation suite, **20/20 consecutive repetitions**;
- peer-ingress lifecycle self-test, **5/5 consecutive repetitions**;
- GCC ASan/UBSan focused authority lane, **5/5**;
- Clang 17 C++20 `-Wall -Wextra -Wpedantic -Werror` syntax checks for all five
  changed C++ translation units;
- optimized GCC Release authority lane, **5/5**, after recorded cloud-window
  resumptions;
- owner-generation audit, **27/27**; process authority, **56/56**; mutex
  capability, **64/64**; transaction-stack authority, **45/45**; payload
  transaction authority, **38/38**; authorizer ownership, **0 violations**.

## Remaining debt and next correction

This is not universal SQLite typing. The deterministic inventory still records
one generic owner-borrow mint, three raw-pointer compatibility declarations, 17
raw prepare sites, 70 raw transaction-control sites, three legacy
`sqlite3_close_v2()` calls, and 104 `sqlite3_open_v2()` sites. The next useful
step is a sealed connection factory that owns path policy, flags, runtime
profile, authorizer, busy handler, and serialized-generation proof, followed by
module-by-module deletion of raw overloads.

The larger architectural debt remains: `src/sync_domain.cpp` is 24,528 lines,
`src/sqlite_replay_ledger.cpp` is 4,466 lines, and the peer-ingress lifecycle is
now 3,833 lines. Decomposition should follow invariant ownership rather than
helper categories. A fault-injecting VFS and executable state oracle are still
needed for power-loss cuts around WAL write/sync/checkpoint, spool rename,
directory sync, durable receipt, and acknowledgement.

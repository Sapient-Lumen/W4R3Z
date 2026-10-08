# Rev0809 online research

This research informed the design and audit. It is not represented as proof of
properties outside the validated local checkpoint scope.

## Stale lock-holder requests require recipient validation

**Primary sources**

- Mike Burrows, *The Chubby lock service for loosely-coupled distributed
  systems*, OSDI 2006: <https://research.google.com/archive/chubby-osdi06.pdf>
- Google Research publication record:
  <https://research.google/pubs/the-chubby-lock-service-for-loosely-coupled-distributed-systems/>
- USENIX publication record:
  <https://www.usenix.org/conference/osdi-06/chubby-lock-service-loosely-coupled-distributed-systems>

Chubby analyzes a stale lock holder whose request reaches a protected service
after another client has acquired the lock. The remedy is not merely detecting
loss in the old client. A sequencer carrying lock identity and generation must
reach the recipient, which rejects stale generations.

**Applied inference:** AnonSync's owner row became a meaningful fence only when
the database minted the generation, orchestration propagated it unchanged, and
each mutation/file-effect recipient compared it with the durable live row.

## SQLite writer serialization

**Primary source:** SQLite, *Transaction*
<https://sqlite.org/lang_transaction.html>

SQLite allows many readers but only one simultaneous writer. `BEGIN IMMEDIATE`
starts a write transaction immediately and may fail with `SQLITE_BUSY` when
another writer is active.

**Applied inference:** A cooperating successor cannot replace the owner row
while a guarded recipient holds the same database's immediate writer
reservation. This makes a local check-plus-mutation interval atomic with
respect to other compliant SQLite writers. It does not create distributed
consensus or bind another database/VFS.

## Proving the check occurs inside a write transaction

**Primary source:** SQLite, *Determine the transaction state of a database*
<https://sqlite.org/c3ref/c_txn_none.html>

`sqlite3_txn_state` reports `SQLITE_TXN_WRITE` when the connection currently has
a write transaction for the selected schema.

**Applied inference:** The focused recipient boundary should reject use outside
a write transaction rather than trusting callers to follow a comment or relying
on an earlier preflight. Rev0809 checks `sqlite3_txn_state(db, "main")` before
loading owner evidence.

## Important non-inferences

These sources do not prove that rev0809 has:

- network or cross-device consensus;
- trusted or synchronized clocks;
- protection against an actor that bypasses the API or rewrites the database;
- Byzantine fault tolerance;
- crash-atomic database-plus-filesystem publication; or
- application-level convergence, privacy, anonymity, or key lifecycle.

## Research-driven next experiment

Build a tiny independent state machine with owner generation, lease time,
ownership mode, daemon pause/resume, recipient mutation, release, takeover,
filesystem publication, and crash points. Generate bounded traces and replay
them against both the pure policy and the SQLite recipient test harness. The
first additional invariant should be:

> Once ownership mode becomes sticky, every guarded mutation either presents
> the exact current live generation or is rejected, including after release and
> restart.

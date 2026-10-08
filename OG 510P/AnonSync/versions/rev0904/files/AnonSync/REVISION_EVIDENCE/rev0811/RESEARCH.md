# Rev0811 research note

Captured 2026-07-17. These sources informed the implementation and the remaining
work; they are not claims that AnonSync implements the cited systems.

## SQLite foreign-key actions

SQLite documents that `ON DELETE CASCADE` propagates deletion of a parent row to
matching child rows. That is exactly why the transient owner-lock row cannot be
the sole durable memory that ownership once existed: deleting the checkpoint
root mechanically deletes the child owner row.

Source: SQLite Foreign Key Support

https://sqlite.org/foreignkeys.html

Design consequence: monotonic owner history must live outside the checkpoint
root's cascade, and tests must execute the real foreign-key action rather than
simulate an absent row.

## SQLite transaction serialization

SQLite documents that `BEGIN IMMEDIATE` starts a write transaction immediately
and may fail with `SQLITE_BUSY` when another writer is active. This supports the
local recipient-fence design: read the durable generation and execute the
mutation on the same writer-reserved snapshot.

Source: SQLite Transaction

https://sqlite.org/lang_transaction.html

Design consequence: this is local serialization for participants sharing the
same database/VFS. It is not network consensus and does not authorize a
preflight read performed before the recipient write transaction.

## `IF NOT EXISTS` is not schema attestation

SQLite documents that `CREATE TABLE IF NOT EXISTS` has no effect when a table or
view with the requested name already exists. It does not verify that the
existing object matches the requested definition.

Source: SQLite CREATE TABLE

https://www.sqlite.org/lang_createtable.html

Design consequence: rev0811's new-table path creates the reviewed geometry, and
row interpretation fails closed on many malformed values, but a hostile or
accidental preexisting object still needs exact `sqlite_schema`, column,
constraint, index, and trigger attestation before it can be treated as an
authority store.

## Recipient-validated fencing generations

The Chubby paper describes sequencers containing lock identity/mode/generation
that a client passes to a server, allowing the server to reject stale requests.
The important transfer is not the particular lock service; it is that freshness
must be checked by the recipient of the protected operation.

Sources:

https://research.google.com/archive/chubby-osdi06.pdf

https://research.google/pubs/the-chubby-lock-service-for-loosely-coupled-distributed-systems/

Design consequence: AnonSync's owner generation is useful only because the
SQLite recipient re-reads the exact live generation in its own write
transaction. A caller-held generation without recipient validation is an
observation, not authority.

## Speculative next experiments

1. Extract the existing schema-token canonicalizer into a smaller shared target
   and make the owner-mode boundary attest exact table SQL plus column and
   trigger geometry before migration or row interpretation.
2. Model owner state independently as a small transition system and generate
   release, expiry, reset, rollback, retry, cascade, and takeover traces for
   differential execution against C++.
3. Make administrative disable a capability-bound transition with a separate
   append-only event and explicit policy/key epoch, rather than a mutable mode
   value alone.
4. Add deterministic crash injection between every owner-mode write, owner-row
   write, root delete, root recreation, commit, and filesystem publication step.
5. Consider a compact fencing token that also binds schema identity and database
   incarnation, but do not let a digest substitute for recipient verification.

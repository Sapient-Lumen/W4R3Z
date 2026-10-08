# Research notes: AnonSync rev0869

Access date for all online sources: **2026-07-21**.

These are design inputs and boundary checks, not proof that the rev0869 owner is
a secure production protocol.

## SQLite transactions

SQLite documents that database reads and writes occur within transactions and
that only one write transaction can exist at a time. `BEGIN IMMEDIATE` attempts
to acquire write authority immediately and may return `SQLITE_BUSY` when another
writer owns it.

- https://sqlite.org/lang_transaction.html

Rev0869 uses one IMMEDIATE transaction for every mutating cutpoint and a
DEFERRED transaction for read-only snapshot/delivery operations. Transaction
atomicity is necessary but not sufficient: the application still has to prove
that all rows in the transaction represent one intended semantic state.

## Foreign keys and PRAGMAs

SQLite foreign-key enforcement is disabled by default for compatibility and
must be enabled per connection. The documentation also states that changing
`PRAGMA foreign_keys` within a transaction has no effect.

- https://sqlite.org/foreignkeys.html
- https://sqlite.org/pragma.html

The owner enables and verifies foreign keys before schema or transaction work,
then runs `foreign_key_check` during every cutpoint load. Foreign keys prove
referential shape, not canonical identity or deterministic projection.

## STRICT tables

STRICT tables constrain declared storage types and reject values that cannot be
losslessly converted to the declared type.

- https://sqlite.org/stricttables.html

That is useful hardening, but it cannot establish that a BLOB is the canonical
encoding of the operation ID beside it. Rev0869 therefore performs exact decode,
rehash, charge remeasurement, and model restore.

## Trigger and schema execution surfaces

SQLite permits TEMP triggers on non-TEMP tables. Such triggers are local to the
connection that defined them, and the documentation recommends schema-
qualifying the target table. Trigger actions execute automatically on the
associated row event.

- https://www.sqlite.org/lang_createtrigger.html

Two design consequences follow:

1. all owner SQL explicitly targets `main.*`, preventing TEMP table/view
   shadowing; and
2. a clean main-schema contract cannot by itself exclude connection-local TEMP
   trigger effects, so staged state is independently reloaded and attested
   before commit.

The additional decision to scan `sqlite_schema.tbl_name` as well as object name
is an implementation inference: attachment target is executable authority, even
when a trigger or index has an unrelated name.

## Atomic commit, WAL, ATTACH, and durability limits

SQLite's atomic-commit and WAL documentation distinguishes logical commit from
power-loss durability. WAL synchronous mode, checkpointing, the WAL companion
files, VFS behavior, and operator copying practices all matter. WAL
transactions spanning multiple attached databases are atomic per database but
not necessarily as one set across host crash.

- https://sqlite.org/atomiccommit.html
- https://sqlite.org/wal.html
- https://sqlite.org/lang_attach.html
- https://sqlite.org/howtocorrupt.html

Rev0869 therefore keeps evidence, projection, mint authority, policy, and outbox
in one `main` database. It does not claim an attested VFS/fsync profile or safe
multi-database crash atomicity. The bundled SQLite version is 3.53.3, newer than
the WAL page's documented 3.51.3 fix for the rare WAL-reset bug, but this is not
a blanket corruption-resistance claim.

## Unsettled sender ownership

AMQP 1.0 transport describes endpoints retaining unsettled delivery state and a
sender removing its delivery tag when it settles—conceptually, when it announces
that it is forgetting the delivery. AMQP transaction state can associate
posting or retiring messages with a transaction.

- https://docs.oasis-open.org/amqp/core/v1.0/csprd01/amqp-core-transport-v1.0-csprd01.html
- https://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-transactions-v1.0-os.html

AnonSync borrows only the ownership lesson: sender intent remains durable until
exact destination/operation acknowledgement. Rev0869 does not implement AMQP,
its link recovery, settlement modes, or transactional resource semantics.

## Design synthesis

The researched boundaries support five rules:

1. use one explicit transaction for one semantic publication cutpoint;
2. configure and verify connection policy before beginning that transaction;
3. treat schema and triggers as executable authority, not passive metadata;
4. keep exact canonical evidence as the source of truth and rebuild summaries;
   and
5. retain sender ownership until exact settlement, while keeping retry state
   bounded and separate from evidence validity.

The next research question is how to prove an incremental point-read/projector
path equivalent to the global restore oracle while adding authenticated actor
and membership authority.

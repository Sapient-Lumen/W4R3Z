# AnonSync rev0770 — SQLite client-data incarnation and authorizer lease

## Mission boundary

AnonSync does not treat a callback installation, pointer address, open handle,
or successful SQL statement as durable authority. Rev0770 concerns only the
process-local capability needed to safely consume already configured SQLite
state. Restart authority remains a separate durable-evidence problem.

## Defect corrected

The rev0769 package claimed three properties that its source did not provide:
connection incarnation, authorizer generation, and use-time ownership probing.
The shipped `PeerTransportIngressSchemaAttestation::authorizes()` compared only
a stored `sqlite3*`; `install_schema_authorizer_or_throw()` installed a callback
with null context. SQLite has one authorizer slot per connection, and a later
call can replace or disable it. Raw allocator addresses can also be reused.
The prior attestation therefore described a stronger boundary than the code
implemented.

## New invariant-owned module

`sync_sqlite_connection_authority` owns all production calls to
`sqlite3_set_authorizer`, `sqlite3_get_clientdata`, and
`sqlite3_set_clientdata`.

Its state contains:

1. a random process salt;
2. a monotonic nonzero connection incarnation;
3. a monotonic nonzero authorizer generation;
4. the exact delegated policy and context; and
5. a one-shot prepare challenge nonce.

The state is attached with `sqlite3_set_clientdata()`. SQLite invokes its
destructor on replacement or connection close. A deliberate reinstall keeps
the same state address, reinstalls the bridge, then advances the generation;
this avoids a callback pointing at deleted state.

## Use-time proof

Acquisition fails closed unless all of the following are true:

- the proof is nonempty;
- the handle exposes a serialized connection mutex;
- the named client-data state exists and passes its internal identity checks;
- process salt and connection incarnation match;
- authorizer generation matches; and
- preparing a fixed statement causes the owned bridge to echo the exact nonce.

The returned move-only lease retains `sqlite3_db_mutex()`. The bridge bypasses
the delegated policy only while preparing the fixed ownership challenge. It
catches every exception and converts unknown policy return values to
`SQLITE_DENY` so no C++ exception or malformed decision crosses SQLite's C ABI.

## Lifecycle integration

Schema verification now returns the lease rather than a boolean-like result.
Every lifecycle consumer stores it through the domain transaction. Each lease
is declared before its `SyncSqliteTransaction`, so C++ reverse destruction
orders statement cleanup and transaction rollback before mutex release even on
exceptions.

The connection is always opened with `SQLITE_OPEN_FULLMUTEX`; a `NOMUTEX`
connection is rejected rather than silently providing a no-op lease.

## Adversarial coverage

The focused suite covers:

- initial install and exact generation one;
- ordinary policy delegation;
- a statement prepared before installation and reauthorized at `sqlite3_step`;
- alien callback replacement;
- callback disablement;
- same-handle generation supersession;
- cross-connection and close/reopen stale proofs;
- malformed and throwing policy callbacks;
- a replacement thread blocked for the full lease, including transaction
  commit; and
- explicit `SQLITE_OPEN_NOMUTEX` rejection.

The peer-ingress schema suite independently proves replacement invalidation,
generation advance, stale-attestation rejection, and recovery.

## What this does not prove

- The token is not durable and must not appear in a receipt or checkpoint.
- Same-process hostile code with unrestricted SQLite access is outside this
  boundary; isolation and API ownership are required.
- The full connection recipe (registered functions, collations, modules,
  db-config state, VFS assumptions) is not yet committed into a versioned
  digest.
- The recognized checkpoint cohost is not yet compared against a canonical
  full expected DDL manifest.
- The durable peer-ingress receipt does not yet bind a schema/recipe digest to
  the payload and claim generation in one evidence envelope.

## Highest next correction

Extract the checkpoint schema from `sync_domain.cpp` into a typed, versioned
module shared by checkpoint creation and peer-ingress cohost verification.
Then commit the exact cohost/connection-recipe digest into the durable ingress
receipt transaction. Do not persist the process-local incarnation.

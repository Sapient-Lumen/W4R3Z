# rev0786 deep audit — observed serialized-generation SQLite authority

## Heart of the mission

AnonSync is an evidence-authorized convergence engine, not a byte copier and
not a collection of successful callbacks. Its central question is: **what exact
evidence authorizes this transition after crash, reuse, concurrency, process
fork, or hostile input?** Durable receipts answer that question across restart.
The C++ owner and borrow types answer a narrower question while a process is
alive: which exact SQLite object generation may this code touch, under which
process and threading preconditions?

## Severe finding

The rev0785 owner-generation borrow proved identity and lifetime but not actual
connection serialization. Typed support and transaction APIs accepted an owner
slot regardless of how its handle had been configured. A caller could open a
`SQLITE_OPEN_NOMUTEX` database, place it in the same owner slot, and reach a
surface whose name and cross-thread tests suggested stronger authority than the
connection possessed.

Checking for a `FULLMUTEX` token at selected open sites would have been a weak
fix. Flags are distant intent, SQLite can be configured at compile/start/run
time, and the owner slot may adopt outputs from many sites. The authority must
be captured where the exact handle becomes the owner's published generation.

## Implemented invariant

1. Every adopted database generation captures an explicit mutex mode and the
   exact `sqlite3_mutex*` identity reported by `sqlite3_db_mutex()`.
2. Empty owner state requires empty evidence. Non-null owner state requires a
   nonzero generation, process provenance, and structurally valid evidence.
3. A borrow compares the exact frozen `{state, handle, process, generation,
   evidence}` tuple under the process-aware lifecycle guard.
4. Process provenance is rejected before shared generation state is touched,
   preserving the post-fork fail-stop boundary.
5. Evidence is captured once and is not refreshed in `get()`, move, reset, or
   release bookkeeping. Those operations remain SQLite-free.
6. `SyncSqliteSerializedDbBorrow` has one checked mint, is move-only, cannot be
   forged from a raw/generic handle, and cannot implicitly decay to
   `sqlite3*`.
7. Typed support helpers and typed transactions require the strict serialized
   capability before executing SQL.
8. Typed statements retain that capability through finalization and expose the
   captured mode only as a read-only projection.
9. Peer-ingress connections retain one owner plus one serialized capability;
   they no longer cache an independent raw database pointer.
10. `NOMUTEX` typed calls reject before authorizer activity, SQL, transaction
    state, or leaked owner pins.

## Important design correction during review

An intermediate design considered calling `sqlite3_db_mutex()` each time a
borrow was used. That looked like stronger live attestation but was the wrong
boundary. For an unserialized connection, concurrent calls into SQLite are
precisely what the type must prevent. Making generic borrow accounting itself
call SQLite would let validation introduce the precondition violation it was
trying to detect. SQLite connection mutex mode is fixed for an open generation,
so the final design captures it atomically with owner adoption and performs
only structural comparisons afterward.

## Refactor findings

The peer-ingress connection records previously had both a process-bound owner
and a cached `sqlite3*`. That duplicate truth made overload resolution and code
review dangerous: a typed call could silently fall back to a raw compatibility
overload. The raw cache is removed. Read/write connection objects retain a
serialized capability, typed transactions receive the owner slot, and narrow C
API calls explicitly derive a raw address from the still-live capability.

The lifecycle unit remains too large. This revision deliberately does not split
it mechanically; the connection factory, schema attestation, retention,
reconciliation, and operator projection should be extracted only when each new
module owns a clear invariant rather than a copied group of helpers.

## Deterministic debt inventory

The revised audit passes 27 required checks while retaining exact migration
debt rather than hiding it:

- 1 generic owner-borrow site (the strict mint itself);
- 3 raw-pointer compatibility declarations;
- 17 raw prepare sites;
- 70 raw transaction-control sites;
- 3 legacy `sqlite3_close_v2()` sites;
- 104 `sqlite3_open_v2()` sites.

These counts are source-shape inventory, not a claim that every listed site is
incorrect. They identify where raw addresses can still bypass typed lifetime or
mode proofs and where future review has the highest leverage.

## What remains missing

The highest-value next change is a sealed `SerializedDbConnection` factory that
binds secure path policy, URI/VFS choice, open flags, runtime profile,
authorizer, busy handler, process incarnation, owner generation, and actual
mutex evidence in one construction path. It should return no raw owner and
should make `NOMUTEX` a distinct type rather than a runtime surprise.

Raw compatibility overloads should then be deleted one aggregate at a time,
starting with the replay ledger and checkpoint/session paths. Every migration
should preserve a typed transaction boundary and exact statement-generation
pin; broad search-and-replace would merely move hidden authority.

The current tests model process death, not storage power loss. A custom SQLite
VFS plus an executable state-machine oracle should inject failure before and
after write, sync, WAL frame, checkpoint, rename, directory sync, receipt
commit, and acknowledgement. Restart state should be compared with the oracle,
including contradiction preservation and bounded recovery.

Privacy also needs an explicit threat model around metadata: peer identifiers,
connection epochs, retry timing, object sizes, operator reports, and historical
incident retention can reveal relationships even when payloads are encrypted.
A useful speculative direction is epoch-scoped pseudonyms and coarse-to-exact
reconciliation evidence, with strict quotas and cryptographic erasure for
expired encrypted spool material.

## Architectural speculation

A coherent capability lattice would make invalid upgrades unrepresentable:

- `DbOwnerGeneration`: unique close authority plus process incarnation;
- `DbBorrow<Serialized>` / `DbBorrow<Unserialized>`: exact-generation use
  authority with immutable observed mode;
- `TransactionGeneration`: one begin/end boundary retaining its DB borrow;
- `StatementGeneration`: exact statement retaining its DB borrow;
- `DurableReceipt`: content/generation-bound evidence reconstructible after a
  crash.

Only an owner publication boundary may mint a database-mode proof. Raw pointers
may be extracted transiently from a live capability but may never mint one.
That separation keeps process-local safety evidence from being confused with
persistent convergence authority.

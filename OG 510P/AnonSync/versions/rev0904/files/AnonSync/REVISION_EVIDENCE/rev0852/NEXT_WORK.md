# AnonSync work after rev0852

## 1. Compose callback teardown at one connection-generation boundary

Keep the busy, progress, authorizer, and client-data owners API-specific, but
add a connection-level orchestrator with named slots, explicit dependencies,
state inspection, and one revoke-all-before-close transition. Generate replace,
revoke, prepare, step/reprepare, failure, and close sequences and compare them
against a small lifecycle model.

## 2. State the mutable-policy synchronization contract

The typed factory proves callback/context agreement, not thread safety. Decide
whether policies must be immutable, externally synchronized, internally atomic,
or invoked only while a documented connection serialization capability is held.
Add negative race-oriented tests and a system-SQLite ThreadSanitizer lane before
making any broad concurrent-teardown claim.

## 3. Split the monolithic build fan-out

`src/sync_domain.cpp` is 15,287 lines and `src/sync_domain_selftests.cpp` is
9,348 lines. Extract the next invariant-owned persistence or transition module
behind a narrow target, move its tests out of the monolith, and measure clean and
incremental compilation edges. Generate repetitive CMake registration from
checked data where that reduces manual inventory drift.

## 4. Make convergence executable

Define a deterministic operation algebra for create, update, delete,
recreation, rename, schema/key epoch changes, and externally visible effects.
Generate duplicate, reordered, partitioned, concurrent, retried, restarted, and
crash-recovered histories. Compare every replica and the C++ implementation
against one compact reference model.

## 5. Build a cross-resource crash oracle

Model SQLite transactions, WAL/checkpoint state, atomic files, directories,
manifests, receipts, and downstream effects as one recovery machine. Inject
cutpoints at every durability-relevant transition and verify accepted recovery
states rather than testing each resource boundary independently.

## 6. Isolate hostile interpretation

Move hostile SQLite and document interpretation into disposable workers using
sealed descriptors, bounded request/response messages, CPU/memory/output/time
limits, restricted filesystem views, and layered syscall controls. Seccomp or
Landlock may contribute to defense in depth but are not complete sandbox proofs.

## 7. Specify privacy, membership, devices, and keys

Define payload encryption, membership, device generations, key epochs,
rotation, revocation, lost-device recovery, rollback resistance, forward
secrecy, post-compromise recovery, metadata leakage, backup custody, and
realistic erasure limits before presenting “Anon” as an implemented property.

## 8. Reduce evidence and audit amplification

Retire lexical audits when typed APIs or semantic oracles make them redundant.
Keep exact inventories only for dangerous primitive ownership and escape hatches.
Stop recursively carrying every historical evidence byte in ordinary handoffs;
retain cryptographic lineage while making the active review surface smaller.

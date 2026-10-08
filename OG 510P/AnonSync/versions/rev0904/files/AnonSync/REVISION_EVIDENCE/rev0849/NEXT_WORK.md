# AnonSync next work after rev0849

## 1. One typed SQLite callback registry

Promote the shared lifetime claim into a connection-owned registry for every
singleton retained callback slot: busy handler, progress handler, authorizer,
commit/rollback/update hooks, trace hooks, and any application-defined callback
whose context address survives the setter call. The registry should expose
named typed leases and encode mutual exclusion, replacement, callback thread
policy, and teardown order. This would replace source-spelling audits with one
runtime ownership boundary.

## 2. Split the large handle-slot header

`sync_sqlite_handle_slot.hpp` is intentionally rigorous but broadly included.
Requiring `SyncSqliteSerializedDbBorrow` in the verification-budget public
header increases incremental rebuild fan-out. Extract a small stable declaration
and borrow interface, or move verification-budget internals behind a private
implementation, without weakening exact-generation ownership. Measure the
translation-unit and rebuild reduction before accepting the refactor.

## 3. Build an executable convergence model

The local integrity kernel is stronger than the distributed semantics. Define a
small deterministic operation algebra for update, delete, recreation, rename,
concurrent mutation, device/key epoch changes, and externally visible effects.
Generate duplicated, reordered, partitioned, retried, and restarted histories;
compare the C++ implementation against a reference model; and state which
operations commute, require causality, or require coordination.

## 4. Cross-resource crash oracle

Unify SQLite transactions/WAL, snapshot bytes, reset receipts, atomic files,
directory barriers, and downstream effect publication in one cutpoint state
machine. Enumerate every durable boundary and verify that recovery either
completes exactly one authorized transition or leaves the prior state intact.
Include injected failures around callback detach and connection close.

## 5. Hostile-input worker isolation

Move untrusted SQLite/document interpretation into disposable workers with
sealed descriptors, bounded request/response framing, CPU and memory ceilings,
wall-clock deadlines, descriptor limits, namespace/filesystem isolation, and a
restricted syscall surface. Treat seccomp and Landlock as defense layers, not as
a complete sandbox claim.

## 6. Privacy and device/key protocol

Before the project name implies anonymity, specify payload encryption,
membership, device generations, key epochs, rotation/revocation, lost-device
recovery, forward secrecy, post-compromise recovery, metadata leakage, backup
custody, rollback resistance, and realistic erasure limits. Keep these claims
separate from local signature and ledger integrity.

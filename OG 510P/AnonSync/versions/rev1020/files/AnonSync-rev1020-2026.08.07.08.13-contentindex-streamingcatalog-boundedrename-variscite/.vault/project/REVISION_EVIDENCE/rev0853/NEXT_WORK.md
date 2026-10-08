# AnonSync work after rev0853

## 1. Build one callback-slot lifecycle orchestrator

Keep API-specific owners, but compose busy, progress, authorizer, client-data,
and future hook slots at one exact connection generation. Model dependencies,
replacement APIs, state inspection, and one revoke-all-before-close transition.
Generate attach, replace, fail, detach, close, and fork sequences against a
small reference state machine.

## 2. Remove raw busy-slot escape hatches by construction

Move the raw timeout overload behind a narrower internal module or capability
and convert remaining raw SQLite connection owners to `SyncSqliteDbHandleSlot`.
Add a reviewed SQL-construction boundary so dynamically assembled
`PRAGMA busy_timeout` cannot evade literal scanning. Consider a debug-only slot
attestation hook without turning normal operation into polling.

## 3. Replace numeric lexical counts with generated registries

The owner-generation audit failure showed that exact source counts amplify
valid changes. Generate dangerous-primitive inventories from one checked data
file or compiler-visible registry, then let CMake and audits consume the same
source of truth. Preserve exact inventories for C escape hatches, not ordinary
typed helper growth.

## 4. Add race-detection lanes

Run a system-SQLite ThreadSanitizer lane where toolchain/runtime compatibility
permits it. Exercise owner attachment, alternate setter rejection, callback
entry, snapshot publication, detach, and connection close. Keep the current
behavioral corpus, but do not treat repeated scheduling as a race detector.

## 5. Split the monolithic build fan-out

Extract the next invariant-owned slice from `sync_domain.cpp`,
`sync_domain_selftests.cpp`, or the replay-ledger monolith. Measure clean and
incremental edges and avoid forcing unrelated translation units to relink for a
small persistence-boundary change.

## 6. Make convergence executable

Define create, update, delete, recreation, rename, schema/key epoch, and
external-effect operations in one deterministic model. Generate duplicated,
reordered, partitioned, concurrent, retried, restarted, and crash-recovered
histories and compare every replica plus the C++ implementation against it.

## 7. Build a cross-resource crash oracle

Treat SQLite transaction/WAL state, atomic files, directory durability,
manifests, receipts, and downstream effects as one recovery machine. Enumerate
cutpoints and accepted recovery states instead of proving each resource in
isolation.

## 8. Specify privacy, devices, membership, and keys

Define encryption, device generations, membership changes, key epochs,
rotation, revocation, lost-device recovery, rollback resistance, forward
secrecy, post-compromise recovery, metadata leakage, backup custody, and
realistic erasure limits before presenting “Anon” as implemented behavior.

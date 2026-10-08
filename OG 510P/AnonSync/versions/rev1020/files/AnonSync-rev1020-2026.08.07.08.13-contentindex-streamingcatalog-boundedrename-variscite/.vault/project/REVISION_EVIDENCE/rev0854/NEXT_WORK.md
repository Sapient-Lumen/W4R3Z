# AnonSync work after rev0854

## 1. Build one callback-slot lifecycle orchestrator

Compose busy, progress, authorizer, client-data, and future hook owners at one
exact connection generation. Model slot dependencies, all setter aliases,
revoke-all-before-close, failed construction, replacement attempts, fork, and
exceptional teardown. Generate histories against a small reference state
machine.

## 2. Eliminate raw callback mutation authority

Move raw callback setters and raw `sqlite3_set_clientdata()` behind narrow
internal capabilities. Convert remaining raw database holders to typed exact-
generation owners. Preserve explicit C escape-hatch inventories, but make
ordinary production code unable to name the primitives directly.

## 3. Add a ThreadSanitizer lane

Use a compatible system-SQLite build and exercise simultaneous attach, callback
entry, snapshot publication, alternate-setter rejection, detach, and close.
Keep the 19,200-race behavioral corpus, but do not treat scheduling repetition as
a race detector.

## 4. Generate dangerous-primitive inventories

Several audits still encode hand-maintained occurrence counts and source
spellings. Generate a checked registry for callback setters, mutex entry/leave,
raw handles, fork sites, and teardown edges; let CMake, audits, and release
evidence consume the same source of truth.

## 5. Split monolithic build fan-out

Extract another invariant-owned slice from `sync_domain.cpp`,
`sync_domain_selftests.cpp`, or `sqlite_replay_ledger.cpp`. Record clean and
incremental build edges so small persistence changes no longer force unrelated
large translation units to rebuild or relink.

## 6. Make convergence executable

Define create, update, delete, recreation, rename, schema/key epoch, and
external-effect operations in a deterministic model. Generate duplicated,
reordered, partitioned, concurrent, retried, restarted, and crash-recovered
histories and compare every replica plus the C++ implementation with that model.

## 7. Build a cross-resource crash oracle

Treat SQLite transaction/WAL state, atomic files, directory durability,
manifests, receipts, and downstream effects as one recovery machine. Enumerate
cutpoints and accepted recovery states rather than proving each resource in
isolation.

## 8. Specify privacy, devices, membership, and keys

Define payload encryption, device generations, membership changes, key epochs,
rotation, revocation, lost-device recovery, rollback resistance, forward
secrecy, post-compromise recovery, metadata leakage, backup custody, and
realistic erasure limits before presenting “Anon” as implemented behavior.

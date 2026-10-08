# Rev0848 deep audit

## Boundary under review

The reviewed boundary is SQLite peer-ingress lock contention: registration of a
`sqlite3_busy_handler`, the callback's mutation authority, connection handoff,
result publication, callback revocation, connection close, and fork inheritance.

## Findings

### 1. Caller-owned result memory was callback-reachable

The former `PeerTransportSqliteBusyHandlerContext` stored a raw pointer to
`SyncPeerTransportSqliteWriteContentionResult`. SQLite could invoke that
callback on whichever thread performed the serialized operation. FULLMUTEX
serializes SQLite calls but does not make unrelated C++ fields atomic or extend
the result object's lifetime. This was a high-severity data-race and dangling
pointer boundary.

**Correction:** the callback reaches only a stable nonmovable owner containing
immutable values and lock-free atomics. Ordinary result publication is a C++
operation outside SQLite and uses saturating, delta-based updates.

### 2. Callback revocation and database close were not one lifetime protocol

A callback owner can be correct in isolation and still dangle if the `sqlite3*`
is closed first. SQLite offers no callback-context destructor for busy handlers.

**Correction:** one exact-generation serialized borrow pins the database while
the callback is installed. A versioned client-data claim makes premature strict
close or named-slot replacement observable as a fail-stop violation. Normal
teardown unregisters the busy handler before clearing the claim and releasing
the borrow.

### 3. Transient state could have become ambient destruction authority

`sqlite3_set_clientdata()` may synchronously run the supplied destructor on
allocation failure, replacement, clearing, or close. Merely marking a claim
`pending` or `detaching` would allow a racing call on another thread to resemble
a legitimate synchronous destruction.

**Correction:** the destructor requires both an allowed atomic state and an
exact-thread TLS witness scoped around the authorized `sqlite3_set_clientdata()`
call. A foreign close/replacement cannot borrow that witness.

### 4. Fork descendants inherited raw addresses without authority

The raw callback address and client-data pointer are copied by `fork()`, while
SQLite explicitly forbids using or even closing a parent-opened connection in
the child.

**Correction:** owner access, callback entry, detach, destruction, raw close,
and client-data replacement all validate process incarnation or fail stopped.
Fresh child-local construction remains permitted and tested.

### 5. Validation architecture rebuilt unrelated monoliths

The lifecycle corpus was reachable only through the large `anonsync_core`
selftest executable. Compiler and sanitizer checks therefore paid for unrelated
sync-domain and replay-ledger corpora.

**Correction:** a minimal focused main links only `anonsync_core_lib`. It is used
for compiler and sanitizer lanes; CTest retains the command-line route to avoid
silently losing dispatcher coverage.

### 6. Package verification did not initially require the new proof boundary

The first final-source audit found that the active projection and manifest could
remain self-consistent even if the newly added owner files were omitted from a
future package.

**Correction:** `verify_release_package.py` now requires the owner header and
implementation, peer-ingress consumer, focused owner test, focused lifecycle
driver, and busy-owner audit. The 32nd busy-owner audit check enforces that
requirement.

### 7. Generated Python bytecode contaminated an intermediate projection

A local `py_compile` check created `tools/__pycache__`. The first patch replay
also used an unstaged Git diff, which omitted new files.

**Correction:** all bytecode was removed, final evidence generation disables
bytecode writes, the package verifier rejects Python caches, and the source
patch is generated from a fully staged parent comparison. Replay matches
**267/267** active files.

## Proof inventory

- busy-handler owner audit: **32/32**;
- retained SQLite mutex capability audit: **70/70**;
- authorizer/client-data inventory: pass, exactly three reviewed production
  client-data owners;
- focused owner runtime: **32/32**;
- persistence process/fork runtime: **31/31**;
- focused peer-ingress lifecycle runtime: **49/49**;
- final CTest registry: **145/145**, including **42/42** audits;
- Clang 17 `-Werror`: **112/112** focused checks;
- GCC ASan+UBSan with leak detection: **112/112** focused checks;
- repeatability: owner **100/100**, process/fork **25/25**, lifecycle **10/10**.

## Residual risk

SQLite has no getter for the installed busy handler. A raw call to
`sqlite3_busy_handler`, `sqlite3_busy_timeout`, or `PRAGMA busy_timeout` can
replace the owner without notifying its client-data claim. Rev0848 makes every
production busy-handler call owner-confined and excludes busy-timeout calls from
peer ingress, but this is structural enforcement rather than a runtime proof.
The next architectural step should be one connection callback registry that
owns every callback setter and prevents raw connection escape.

The owner also assumes teardown is quiescent. FULLMUTEX serialization makes
sequential handoff valid; it does not legalize racing object destruction. No
ThreadSanitizer or full-project sanitizer claim is made.

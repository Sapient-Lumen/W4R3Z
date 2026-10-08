# AnonSync rev0851 audit

## Audit target

This revision audits the lifetime of application policy state retained behind
SQLite's authorizer bridge. The reviewed transition is:

1. construct a process-bound policy/context capability;
2. acquire the exact serialized SQLite connection generation;
3. publish policy-empty connection client data;
4. attach the authorizer lifetime claim;
5. transfer policy ownership into the live state;
6. install and challenge the callback;
7. serialize replacement or revocation under the connection mutex;
8. disable the callback before retiring policy state;
9. move retired state into an ordinary C++ escrow;
10. leave SQLite's mutex; and
11. release the context and any application custom deleter.

## Findings corrected

### Critical: non-null policy context was a borrowed retained address

The public API accepted an arbitrary raw `void*` while SQLite could invoke the
bridge after the installing stack frame ended. Connection generation and bridge
state were protected, but the policy referent was not owned. Rev0851 makes
non-null context installation require `SyncSqliteOwnedAuthorizerPolicy`, and the
legacy overload rejects non-null borrowing.

### High: application destruction could run under SQLite's mutex

Replacement and close need SQLite serialization, but user-provided shared
context deleters are arbitrary code. The old raw API could not specify where
cleanup occurred. Rev0851 declares retirement escrow before the mutex guard and
uses reverse C++ local destruction so the mutex is left first. Executable
worker-thread probes call `sqlite3_mutex_try()` from custom deleters and observe
`SQLITE_OK` on both replace and revoke.

### High: fork could touch copied ownership metadata

A copied `shared_ptr` control block is not a child-process lifetime authority.
The new owner validates immutable process incarnation before invocation,
inspection, movement, swap, or destruction. Fork-adversarial probes demonstrate
fail-stop behavior before shared ownership is touched.

### Medium: the new test initially bypassed process-topology ownership

The first focused test used raw `fork()` directly, creating a second primitive
owner. The complete registered audit caught it. The test now uses
`spawn_inherited_test_process_or_throw`; the raw primitive remains confined to
`tests/inherited_test_process.cpp`. This is a useful example of a source audit
preventing a local test convenience from widening global architecture.

## Composition review

The connection state owns the policy capability rather than a raw context. New
state is deliberately policy-empty while SQLite may destroy client data during
allocation failure. Replacement leaves the old policy in an outer escrow.
Revocation disables the authorizer, destroys its named callback claim, empties
policy state, and clears client data before strict close. State destruction
fails stopped if callback attachment or policy remains.

The callback bridge catches policy exceptions at the C boundary and denies the
operation. The owner itself rejects null callbacks and invalid empty/context
shape. The context-free compatibility form remains available without creating a
synthetic shared allocation.

## Audit and test result

- owned policy runtime: **20/20**;
- raw authorizer owner runtime: **20/20**;
- integrated connection authority: **153/153**;
- transaction exception composition: **37/37**;
- allocator-fault campaign: **642/642**;
- process/fork authority: **44/44**;
- peer schema authority: **66/66**;
- focused runtime total in each compiler/sanitizer lane: **982/982**;
- focused structural audit total: **356/356**;
- complete registered test gate: **148/148**, including **43/43** audits.

## Remaining risk

Type erasure does not prove callback/context type agreement. Shared ownership
does not synchronize mutable policy state. A new child-process owner cannot
prove pre-fork provenance of a supplied control block. Foreign raw authorizer
replacement remains source-inventory constrained between nonce probes. General
concurrent close/use races, TSan, Windows, full-project sanitizers, and bundled
SQLite instrumentation remain outside this revision.

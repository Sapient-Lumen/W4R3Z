# AnonSync rev0854

## Mission increment

AnonSync's implemented heart is to turn each untrusted observation and each
state-changing API into the narrowest process-, thread-, connection-,
generation-, lifetime-, policy-, resource-, namespace-, and durability-bound
capability that may authorize one transition. Serialization is not merely a
performance property: when multiple APIs mutate one retained callback slot, the
exact serializer must be explicit transition authority.

Rev0854 makes the SQLite connection mutex a typed witness for retained callback
claim publication and revocation.

## Severe defect corrected

The busy-handler, verification-progress, and authorizer owners each used a named
`sqlite3_set_clientdata()` sentinel to own callback-context lifetime. SQLite's
individual API calls were serialized on `FULLMUTEX` handles, but the logical
transition remained split:

1. observe the named client-data slot as empty;
2. allocate and publish a pending claim;
3. install the singleton callback.

Two legitimate constructors could interleave between those steps. Both could
observe the slot as empty; the later `sqlite3_set_clientdata()` could replace
and synchronously destroy the other constructor's pending or live sentinel.
The fail-stop destructor correctly treated that replacement as a lifetime
violation, but the system had converted ordinary duplicate attachment into a
process-wide exit rather than one winner and one recoverable rejection.

Rev0853's busy-timeout fence protected owner-versus-alternate-setter races. It
did not protect owner-versus-owner races, and the same split existed in all
three retained callback protocols.

## Delivered C++ boundary

- Added `SyncSqliteDatabaseMutexGuard`, an independently linked, noncopyable,
  nonmovable owner for one recursive `sqlite3_db_mutex()` entry.
- Bound each guard object to the current process incarnation and exact C++
  thread incarnation; destruction and one-way transfer reject execution after
  fork or on another thread before leaving SQLite-owned state.
- Required serialized/FULLMUTEX handles for authority-bearing use.
- Preserved a deliberately nonauthorizing `PermitUnserialized` lane for the
  reviewed single-user `NOMUTEX` busy-timeout compatibility gateway.
- Added exact-database authorization: a guard for another handle, an empty
  guard, or the NOMUTEX compatibility lane cannot authorize a callback claim.
- Changed `SqliteRetainedCallbackClaim::attach`, `require_live`, and `detach`
  signatures to require the exact live guard. Omitting the critical-section
  witness is now a compile error rather than an audit-only convention.
- Held one guard across the complete claim-plus-callback-setter transition in
  `SqliteBusyHandlerOwner`, `SqliteVerificationBudget`, and
  `SqliteAuthorizerOwner`.
- Held the same guard across liveness proof, callback revocation, and claim
  destruction during teardown.
- Kept exact database-generation borrows alive until after the guard leaves the
  SQLite-owned mutex.
- Replaced the local `DbMutexGuard` in connection authority and the local
  `SqliteDatabaseMutexScope` in support code with the shared owner.
- Retained manual mutex enter/leave only for the separately reviewed
  longer-lived connection-authority lease.

## Runtime proof

Each singleton callback owner now has a 64-iteration simultaneous-construction
oracle. Two contenders start together against one exact serialized connection;
exactly one constructor succeeds, exactly one receives the expected ordinary
`std::logic_error`, the live winner remains callable, teardown removes the exact
claim, and no generation borrow leaks.

Direct guard tests cover:

- null handle and empty-label rejection;
- exact connection-mutex identity;
- recursive composition;
- competing-thread exclusion and later admission;
- one-way transfer of the exact entered mutex;
- strict `NOMUTEX` rejection; and
- the explicit nonauthorizing NOMUTEX compatibility lane.

The repeatability lane executed the busy, verification, authorizer, and support
corpora 100 times each: **400/400** process runs and **19,200** simultaneous
duplicate-owner race iterations.

## Audit/refactor work

- Expanded the SQLite mutex-capability audit to treat the new guard as the sole
  scoped mutex owner and connection authority as the sole manual retained-lease
  owner.
- Required all three client-data claim methods to carry the exact guard in their
  type signatures and all three callback owners to consume it around complete
  slot transitions.
- Expanded the busy-handler, verification-budget, authorizer, and process
  authority audits for the serialized race and teardown order.
- Made the new guard, direct runtime proof, and composed audits mandatory in
  release packages beginning with rev0854 while retaining verification of the
  sealed rev0853 parent.
- Corrected a brittle authorizer audit that required one null-input expression
  on a single physical line. It now recognizes the same semantic guard across
  arbitrary whitespace, reducing format-only audit failures.
- Preserved a narrow direct-call inventory: scoped `sqlite3_mutex_enter/leave`
  lives in the guard; manual retained-lease entry/leave remains in connection
  authority.

Focused structural results are **311/311**:

- SQLite mutex capability: **77/77**;
- busy-handler owner: **38/38**;
- verification budget: **63/63**;
- authorizer owner: **42/42**; and
- SQLite process authority: **91/91**.

## Validation

The final active source passes:

- a complete GCC 14.2 C++20 Debug Ninja all-target graph, completed across
  resumed invocations without intervening source changes, followed by a final
  true `ninja: no work to do` dependency closure;
- all **148/148** registered CTest entries in five exact non-overlapping ranges,
  including all **43/43** registered audits;
- **455/455** focused runtime checks under GCC Debug;
- **455/455** focused checks after Clang 17 compilation with `-Werror`;
- **455/455** focused checks under GCC 14 ASan+UBSan with leak detection and
  halt-on-error behavior;
- **400/400** repeatability executions with **19,200** concurrent duplicate-slot
  races;
- rev0853 parent verification at **26/26** ZIP checks and **22/22** extracted
  directory checks; and
- exact active-source patch replay and package projection verification recorded
  in `REVISION_EVIDENCE/rev0854/`.

Two attempted parallel complete-registry invocations were interrupted by the
cloudtainer command ceiling after only passing output; one uninterrupted
148-test invocation is therefore deliberately not claimed. The exact ranges
were 1-34, 35-55, 56-77, 78-114, and 115-148, covering every registered test
once without overlap.

## Boundaries not claimed

This is source-confined composition, not universal SQLite interposition.
Foreign code holding a raw `sqlite3*` can still invoke alternate callback
setters, same-name client-data replacement, or close/use APIs outside the typed
protocol. Arbitrary concurrent owner-object method calls remain a caller-level
C++ lifetime violation even where SQLite itself is serialized.

The guard proves the lifetime and execution of its own mutex entry. It does not
by itself prove that a raw database handle was not inherited across `fork()`;
exact-generation process-bound owners must reject that handle before guard
construction.

Bundled SQLite was not sanitizer-instrumented. ThreadSanitizer, full-project
sanitizers, Release all-target behavior, Windows runtime behavior, distributed
convergence, confidentiality, anonymity, metadata hiding, forward secrecy,
post-compromise recovery, hostile-worker isolation, and secure erasure are not
claimed.

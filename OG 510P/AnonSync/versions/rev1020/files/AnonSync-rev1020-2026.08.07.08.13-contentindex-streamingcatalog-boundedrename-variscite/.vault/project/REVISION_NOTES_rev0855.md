# AnonSync rev0855

## Mission increment

AnonSync's implemented heart is to turn each untrusted observation and each
state-changing API into the narrowest process-, thread-, connection-,
generation-, lifetime-, policy-, resource-, namespace-, and durability-bound
capability that may authorize one transition. Compatibility with a weaker
external contract must not silently acquire the type surface of a stronger
authority.

Rev0855 separates SQLite callback-transition authority from the legacy raw
busy-timeout compatibility fence and makes teardown affinity unconditional.

## Severe defects corrected

Rev0854's `SyncSqliteDatabaseMutexGuard` accepted a
`SyncSqliteDatabaseMutexRequirement` enum. `RequireSerialized` rejected a null
connection mutex; every other representation—including an invalid value
introduced through a cast—followed the permissive lane. The same object exposed
`authorizes()`, mutex identity, and `release()`, so a single type represented
both strict retained-callback authority and a narrow nonauthorizing NOMUTEX
compatibility case.

The destructor then began with:

```cpp
if (mutex_ == nullptr) return;
```

That return preceded process- and exact-thread validation. A NOMUTEX guard could
be copied by `fork()` or handed to a foreign C++ thread and destroyed without
reaching the capability fail-stop path. A strict guard also lost destructor
execution-affinity enforcement after `release()` set its mutex pointer to null.
The mutex itself might have moved to a typed lease, but the guard object's
remaining lifetime was still bound to the exact acquiring execution context.

## Delivered C++ boundary

- Removed `SyncSqliteDatabaseMutexRequirement` and every runtime policy branch
  from `SyncSqliteDatabaseMutexGuard`.
- Made the strict guard unconditionally require a serialized/FULLMUTEX
  connection.
- Retained exact-database `authorizes()`, mutex identity, and one-way `release()`
  only on the strict type.
- Added `SyncSqliteBusyTimeoutMutationGuard`, a noncopyable and nonmovable owner
  used only by `sqlite_set_busy_timeout_or_throw()`.
- Allowed the narrow owner to enter a FULLMUTEX connection mutex or admit a
  caller-controlled NOMUTEX handle under SQLite's external single-user
  contract.
- Deliberately omitted callback authorization, mutex identity, and transfer
  operations from the compatibility owner.
- Added a separately linked `require_current_sync_sqlite_execution_noexcept()`
  helper that checks process incarnation before exact thread incarnation.
- Made both destructors call the shared validator before any null-mutex branch.
- Kept strict `release()` process- and thread-bound and retained destructor
  affinity after transfer.
- Updated the invariant-owned CMake source inventory so the helper and narrow
  owner cannot disappear from reviewed builds.

## Runtime and compile-time proof

The focused support corpus now proves:

- the strict owner satisfies exact-database callback-witness and transferable
  mutex concepts;
- the compatibility owner satisfies neither concept;
- both owners reject null handles and empty labels;
- the strict owner rejects NOMUTEX connections;
- the narrow owner preserves the reviewed single-user NOMUTEX busy-timeout
  operation; and
- existing recursive composition, competing-thread exclusion, exact mutex
  identity, and transfer behavior remain intact.

The process/fork corpus now executes three direct fail-stop regressions:

1. deleting a NOMUTEX busy-timeout mutation guard on a foreign thread;
2. deleting a copied NOMUTEX guard in an inherited process; and
3. deleting a strict guard on a foreign thread after its mutex entry has been
   transferred with `release()`.

All three previously reached the early return or equivalent null-mutex shape;
all three now exit through the process/thread capability violation boundary.
The parent still tears down its own NOMUTEX guard normally.

## Audit and refactor work

- Expanded the SQLite mutex-capability audit to recognize two disjoint scoped
  owners and to require that only the strict owner can authorize retained
  callback claims or transfer mutex ownership.
- Required the shared process-then-thread validator in both owners and direct
  runtime proof for the null-mutex and post-transfer destructor cases.
- Expanded the SQLite process-authority audit to bind the new sources and the
  fork/thread regressions.
- Expanded the busy-handler audit to require the narrow owner at the sole direct
  production `sqlite3_busy_timeout()` gateway.
- Changed the busy API call inventory to strip `//` comments before matching;
  documentation that mentions `sqlite3_busy_timeout()` no longer inflates the
  production C API inventory.
- Made the release verifier require the new helper, owner, and process proof from
  rev0855 onward while preserving verification of the sealed rev0854 parent.

The focused audit totals are:

- SQLite mutex capability: **79/79**;
- busy-handler ownership: **39/39**;
- SQLite process authority: **93/93**;
- verification budget: **63/63**; and
- authorizer ownership: **42/42**.

Total: **316/316**.

## Validation

Final-source validation completed successfully:

- GCC 14.2 C++20 Debug all-target build and immediate true zero-action Ninja
  closure;
- **148/148** registered CTests in exact ranges 1–34, 35–55, 56–77, 78–114,
  and 115–148;
- **43/43** registered structural audits;
- six focused GCC Debug executables: **461/461** checks;
- the same six targets compiled with Clang 17 and `-Werror`, then passed
  **461/461** checks;
- GCC 14 AddressSanitizer plus UndefinedBehaviorSanitizer, leak detection and
  halt-on-error: **461/461** checks;
- generated Ninja compile and link commands independently contain
  `-fsanitize=address,undefined` for the focused C++ boundary;
- **600/600** repeatability process runs, 100 executions of each focused
  executable, representing **46,100** aggregate check observations;
- rev0854 parent archive SHA-256
  `a54e493f3eea8aa8923d5f1815f3ed377eb5bfe1286befde7e8b1c1dae49eeed`;
- parent verification: **26/26 ZIP** and **22/22 directory** checks; and
- exact source-patch replay against the verified parent followed by active-file
  comparison.

## Boundaries not crossed

The NOMUTEX compatibility guard is not a synchronization mechanism. It assumes
the caller already provides SQLite's required single-user discipline. It only
makes the C++ guard lifetime process- and exact-thread-bound and prevents that
compatibility type from being used as retained callback authority.

Arbitrary foreign users of raw `sqlite3*`, arbitrary concurrent close or object
teardown, ThreadSanitizer, bundled-SQLite sanitizer instrumentation,
full-project sanitizers, Release all-target behavior, Windows runtime behavior,
distributed convergence, confidentiality, anonymity, metadata hiding, forward
secrecy, post-compromise recovery, hostile-worker isolation, and secure erasure
are not claimed.

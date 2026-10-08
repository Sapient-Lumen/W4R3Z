# AnonSync rev0849

## Mission increment

AnonSync's implemented heart is to freeze an observation into the narrowest
process-, thread-, connection-, generation-, and resource-bound capability that
can authorize one deterministic recoverable transition. A C API that retains a
raw C++ address therefore creates an authority edge: the address must not
outlive its object, cross an unproved process or thread boundary, survive its
connection generation, or be silently replaced before explicit revocation.

Rev0849 generalizes that rule from the busy handler to SQLite retained callback
contexts as a class. It also moves resident snapshot verification and pending
report cleanup onto exact-generation typed database ownership.

## Severe defects corrected

The verification-budget progress handler retained `this` through
`sqlite3_progress_handler()` while its database was represented only by a raw
`sqlite3*`. The class enforced exact thread use but did not pin the connection
generation or attach a connection-owned destruction sentinel. Premature close,
client-data replacement, or a close/reopen generation transition could
invalidate the callback context before ordinary C++ teardown detected it.

The pending-effect report error path contained a more direct lifetime fault.
An inner catch detached the progress handler and best-effort closed the raw
handle, then rethrew into an outer catch that could close the same non-null raw
pointer again. On an immediately destroyed connection this is a double-close
use-after-free. Typed `SyncSqliteDbHandleSlot` reset makes consumption explicit
and idempotent, and cleanup is now ordered as callback detach, transaction
rollback, then one owner reset.

The busy-handler client-data sentinel was also a one-off implementation. Keeping
separate copies of the same state machine and exact-thread destruction witness
would make future retained callback owners drift. Rev0849 extracts one focused
owner and makes both busy and progress handlers consume it.

## Delivered

- Added noncopyable, nonmovable `SqliteRetainedCallbackClaim` as a separately
  linked C++20 persistence boundary.
- Froze the named client-data key before publication and rejected empty or
  NUL-containing names and duplicate live claims.
- Bound each claim to the current process incarnation and a separately allocated
  magic/self-checked state object.
- Required both an explicit `registration_pending`/`live`/`detaching` state and
  the exact thread-local `sqlite3_set_clientdata()` witness before SQLite may
  destroy a claim during registration failure or detach.
- Turned connection destruction or same-name replacement while live into a
  fail-stop capability violation.
- Refactored `SqliteBusyHandlerOwner` to compose the shared claim instead of
  duplicating its state machine, TLS witness, and destructor callback.
- Changed `SqliteVerificationBudget` construction to consume
  `SyncSqliteSerializedDbBorrow`; a raw handle can no longer mint production
  progress-handler authority.
- Ordered progress-handler teardown as live-claim proof, callback disable,
  client-data detach, then exact-generation borrow release.
- Added `SealedSqliteSnapshot::open_database_owner_or_throw()` and migrated
  production resident-snapshot readers to typed handle slots.
- Reworked prefix-continuity and pending-report paths so statement, callback,
  transaction, and connection authority are consumed exactly once.
- Added direct tests for claim input freezing, duplicate/occupied claims,
  idempotent detach, raw immediate close, deferred close-v2 zombie destruction,
  same-name replacement, owner reset with a live borrow, typed snapshot opens,
  and fork-descendant misuse.
- Updated the SQLite snapshot, verification budget, busy handler, mutex,
  process-authority, raw-fork, self-exec, inherited-process, and release-package
  audits.

## Validation

The final source passes a fresh GCC 14.2 Debug all-target build and a true
zero-work dependency closure; all 145 registered tests in five exact
non-overlapping ranges; all 42 registered source audits; focused GCC runtime
checks; Clang 17 `-Werror` focused compilation and runtime; GCC ASan+UBSan
focused runtime with leak detection; 260 repeated focused executions; sealed
parent package verification; and exact source-patch replay across all 269 active
files. Exact details and scope limits are in
`REVISION_EVIDENCE/rev0849/validation/VALIDATION_SUMMARY.json`.

## Scope limits

This revision does not prove that arbitrary third-party code cannot replace a
progress handler: SQLite exposes one progress handler per connection and no
getter. Production source inventory remains the enforcement boundary. A raw
`sqlite3_close_v2()` can also return success while outstanding SQLite objects
keep a zombie connection alive; typed ownership rejects the reviewed close path
immediately, while the client-data claim fails stopped when a raw deferred
violation eventually destroys the connection.

No claim is made here for all callback APIs, arbitrary concurrent teardown,
ThreadSanitizer, full-project sanitizer coverage, Windows runtime behavior,
power-loss completeness, distributed convergence, confidentiality, anonymity,
metadata hiding, forward secrecy, post-compromise recovery, or secure erasure.

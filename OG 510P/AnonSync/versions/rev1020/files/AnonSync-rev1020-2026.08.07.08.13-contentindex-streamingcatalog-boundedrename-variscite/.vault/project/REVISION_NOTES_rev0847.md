# AnonSync rev0847

## Mission increment

AnonSync's implemented heart is converting an observation into the smallest
capability that can authorize one deterministic, recoverable transition. That
requires more than verifying bytes or acquiring a library mutex. The authority
must also bind the process and exact thread lifetime that own every ordinary C++
field, callback context, detach operation, and destructor side effect.

Rev0847 applies that rule to `SqliteVerificationBudget`. The budget installs
itself as SQLite's `sqlite3_progress_handler` context and mutates ordinary row,
byte, and step counters. Before this revision it captured a process incarnation
but no exact thread incarnation. A serialized/FULLMUTEX SQLite connection can
serialize calls from multiple threads; that does not transfer ownership of the
raw callback context or make the budget's ordinary fields cross-thread owners.

The budget now captures process authority first and exact thread authority
second. Every throwing operation rejects an unauthorized execution context
before reading the private diagnostic label or any mutable state. Callback,
accessor, detach, and destructor paths are `noexcept` and fail stopped on an
invalid or foreign process/thread capability.

## Severe defect corrected

The pre-revision contract admitted sequential foreign-thread use. A different
thread could call a FULLMUTEX-protected SQLite operation, enter the progress
callback with the budget's raw `this` pointer, and update counters even though
no C++ lifetime or thread-ownership transfer had occurred. Destruction or
handler detachment on a foreign thread had the same authority gap. Concurrency
could additionally form a C++ data race before the old process-only guard had
any chance to help.

The first rev0847 guard revision still formed a `string_view` over the
caller-supplied diagnostic label before confirming thread authority. Although it
did not mutate protected state, this weakened the intended rejection boundary
and could disclose private diagnostic text to an unauthorized thread. The final
guard consults only immutable process/thread capability tokens until authority
is established and uses a static public boundary name in rejection messages.

## Delivered

- Bound `SqliteVerificationBudget` to both `SyncProcessIncarnation` and
  `SyncThreadIncarnation`.
- Preserved process-before-thread validation order so inherited-process failure
  remains unambiguous and post-fork thread bytes are never accepted as primary
  authority.
- Centralized the mandatory pair in
  `require_current_execution_or_throw()` and
  `require_current_execution_noexcept()`.
- Made invalid as well as mismatched `noexcept` capabilities fail stopped.
- Prevented unauthorized throwing calls from reading or echoing the budget's
  private diagnostic label.
- Added direct proofs that a foreign throwing call leaves all counters unchanged
  and the originating thread remains authorized.
- Added inherited-process death probes for foreign-thread SQLite callback entry,
  progress-handler detach, and destruction; each must exit with the reviewed
  process-capability violation status 86.
- Added the budget death corpus to the exact inherited-process inventory. The
  final independently discovered inventory is 12 consumer translation units,
  21 spawn sites, one centralized test-only raw `fork()`, and zero production
  raw forks.
- Reworked `audit_sqlite_verification_budget.py` around a brace-aware C++
  function extractor that skips comments, ordinary strings, character literals,
  and raw strings instead of using brittle next-function text slicing.
- Promoted the focused budget test and architecture audit to mandatory release
  package members.

## Audit/refactor result

The audit refactor found a stale duplicated fork inventory in the self-exec
audit. The dedicated inherited-process and raw-fork audits correctly discovered
12 consumers and 21 spawn sites after the new death corpus, while the self-exec
audit still asserted rev0846's 11/20 counts. The duplicate was aligned and the
shared topology owner remains the only test raw-fork implementation.

The new SQLite budget audit reports **53/53** checks. The adjacent generic
thread-incarnation audit reports **33/33**, SQLite process-authority audit
**87/87**, raw-fork audit **11/11**, inherited-process audit **15/15**, and
self-exec audit **36/36**.

## Validation

The exact record is in
`REVISION_EVIDENCE/rev0847/validation/VALIDATION_SUMMARY.json`.

The final active source passed:

- a complete GCC 14.2 Debug all-target build of 233 compile/link steps;
- a final rebuild from the exact source state followed by normal and dry-run
  Ninja closure with no remaining work;
- one uninterrupted complete CTest invocation: **143/143**, including
  **41/41** registered source/architecture audits;
- Clang 17 with `-Werror` on the four affected ownership/process targets,
  **128/128** direct checks;
- GCC 14 AddressSanitizer plus UndefinedBehaviorSanitizer with leak detection on
  the same focused targets, **128/128** direct checks; and
- 100 consecutive executions of the 70-check verification-budget corpus.

The source patch changes 11 active files with 447 insertions and 56 deletions.
It replays exactly on the sealed rev0846 parent and matches all 262 active files.

## Scope limits

Thread affinity is not synchronization. The token rejects sequential misuse and
fail-stops selected `noexcept` misuse, but it cannot legalize a caller that races
an object's fields or lifetime before the check. No ThreadSanitizer claim is
made. The sanitizer lane is focused, not full-project.

The fail-stop destructor contract is intentionally severe: violating ownership
terminates the process rather than attempting cross-thread callback teardown.
This is safer than silently touching a potentially live raw callback context,
but shared ownership would require a different design—normally a serialized
executor, explicit synchronization, and a lifetime protocol.

This revision does not prove every SQLite callback or user-data owner in the
cube is correctly bound. It does not claim Release all-target coverage, Windows
runtime, arbitrary post-fork library re-entry, hostile-input process isolation,
full cross-resource crash completeness, distributed convergence, payload
confidentiality, anonymity, metadata hiding, forward secrecy, post-compromise
recovery, or secure erasure.

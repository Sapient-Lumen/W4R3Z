# Revision notes: AnonSync rev0863

## Mission increment

A transaction-wide SQLite VM budget does not bound time spent waiting for a
lock, because the progress callback does not run while the connection is
blocked. Rev0863 gives checkpoint-sidecar hydration a separate exact-generation
lock-wait owner and makes its sleep authority cumulative across the complete
transaction lifetime.

## Principal corrections

1. Changed `SqliteBusyHandlerOwner` from per-locking-event elapsed-time renewal
   to one cumulative requested-sleep allowance for the complete owner lifetime.
2. Consumed sleep authority before `sqlite3_sleep()`, preventing scheduler delay
   or later locking events from silently reminting budget.
3. Added `SyncSqliteSidecarLockWaitBudget`, a final, noncopyable, nonmovable
   exact-generation adapter separate from the progress-handler execution budget.
4. Kept one busy callback alive across transaction begin, every statement,
   commit, and failure-path rollback while preserving progress-callback
   revocation before cleanup.
5. Added a zero-wait fail-fast policy, a reviewed 60-second maximum, sticky typed
   exhaustion evidence, and distinct authorized-versus-observed sleep
   diagnostics.
6. Preserved native `SQLITE_BUSY` when SQLite bypasses the busy handler for
   deadlock avoidance; only callback-proved exhaustion is translated.
7. Added cross-event, exact-generation, cleanup-order, reuse, public-policy, and
   transaction-level lock-contention regressions.
8. Corrected a brittle audit literal uncovered by the uninterrupted registry
   run and made the audit assert the actual zero/fail-fast contract.
9. Found and closed a sanitizer-graph gap: the retained busy owner was
   instrumented but its mutex/affinity dependency library was not. All selected
   first-party C++ compilation commands are now ASan+UBSan instrumented.

## Compatibility

No wire, digest, manifest, workorder, checkpoint, or durable-document spelling
changes. The public recovery limits and results gain additive lock-wait policy
and diagnostic fields. Valid uncontended work is unchanged. Lock conflicts may
now fail earlier once the one transaction-wide requested-sleep authority is
consumed.

## Validation summary

GCC 14.2 Debug all-target closure; one uninterrupted 162/162 registered-test
campaign including 49/49 audits; focused 47-check busy-owner and 45-check
sidecar corpora; 611-check domain model; 100 ordinary repeats of both focused
corpora and both structural audits; Clang 17 `-Werror` focused and integrated
runtime; GCC 14 ASan+UBSan focused and domain runtime with leak detection plus
25 focused repeats; exact replay of the 13-file delta across all 311 active
files; sealed-parent verification 26/26 ZIP and 22/22 directory.

## Deliberate nonclaim

The limit is exact cumulative `sqlite3_sleep()` request authority, not a hard
wall-clock deadline. Scheduler latency may exceed it, SQLite may skip the busy
handler to avoid deadlock, and filesystem or device I/O is not bounded by this
callback. This revision does not claim that every SQLite path is lock-budgeted,
that the bundled SQLite C amalgamation is sanitizer-instrumented, or that the
product already provides distributed convergence or anonymity.

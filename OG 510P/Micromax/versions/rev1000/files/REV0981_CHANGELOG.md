# Rev0981 changelog — finite process-start handoff

## Worker startup owner

- Deferred multiprocessing Process construction into the same owner as
  `Process.start()`.
- Added a separate normalized startup timeout and
  `WorkerResultStartTimeoutError`, preserving existing timeout mappings.
- Applied one absolute deadline across waiting for the start gate and the
  process constructor/start phase.
- Added a completion-time witness so just-late starts cannot win an event-wait
  race.
- Limited the process to one unresolved starter; normal starts release the gate
  before result collection continues.
- Transferred channel/process/abnormal-cleanup ownership to a timed-out starter,
  which reclaims any late child before releasing the gate.

## Context policy

- Removed the single-native-task `fork` fallback because deadline-owned startup
  necessarily creates another thread.
- Kept spawn first and forkserver second for importable entrypoints.
- Kept the explicit nonpositive direct path for non-importable shell/REPL
  embeddings and rejected an explicit fork context at the bounded owner.
- Updated the legacy multiprocessing regex adapter to use the same policy.

## Audit and evidence

- Extended `tools/reproduce_process_start_stall.py` to compare raw blocking with
  bounded caller return, late cleanup, and post-stall recovery.
- Added deterministic blocked-constructor, blocked-start, one-pending retry,
  absolute-deadline, late-boundary, cleanup, and gate-recovery regressions.
- Reworked fork-inheritance-dependent filesystem/save tests to preserve the
  foreground TOCTOU contracts and test worker error projection independently.
- Corrected the compatibility export's module-docstring placement and exported
  the new startup contract.
- Extended `mxaudit` with an executable worker-start boundary check covering
  deferred construction, the absolute deadline, late ownership, and fork
  rejection.
- Added `docs/938-worker-start-deadline-single-pending-handoff.md` with primary
  Python/CPython research, measurements, and deliberately narrow residuals.

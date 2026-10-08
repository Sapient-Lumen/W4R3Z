# Rev0982 changelog — Popen deadline and sparse hot paths

## Process availability

- Added `micromax.subprocess_start` with one absolute constructor deadline, one
  unresolved-start ceiling, completion-time classification, and exact late
  cleanup handoff.
- Routed regex-worker `Popen` construction and readiness through one startup
  lease.
- Routed bounded argv/shell construction and execution/capture through one
  operation lease; constructor timeout maps to 124 and failure to 127.
- Reused existing process-tree, capture-pipe-owner, stream-close, and reap logic
  for processes that appear after caller timeout.
- Made completed-child handoff interruption-safe, treated interrupted starter
  identity publication conservatively, and kept partial capture-reader startup
  inside the process owner so started threads are joined during teardown.
- Added a deterministic standalone constructor-stall witness.

## Editor hot paths

- Added checkpointed `WordWrapLayout` with a 256 KiB retained checkpoint ceiling
  and a four-entry per-buffer LRU in `VisualRowIndex`.
- Changed true-wordwrap cursor, inverse, viewport, and rendering paths to use the
  shared sparse layout and materialize visible bounds only.
- Packed search line starts and span starts/ends in `array('Q')`; literal scans
  write directly to final storage and bounded representations avoid debug cliffs.
- Added compact `ReplacementEdit` plans; full rich match rows are now a
  compatibility/sample projection and newline coordinates use one forward walk.
- Changed interactive query-replace to retain compact immutable edits and recover
  old source slices lazily.
- Reused caller-owned compact line indexes in simultaneous edits and replaced
  Python per-character line indexing with repeated native newline searches.

## Audit and evidence

- Added permanent Python-allocation and constructor-stall evidence tools.
- Added sparse/reference geometry, million-character storage cap, cache reuse/
  eviction, packed storage, bounded repr, no-rebox, shared-deadline, and late
  cleanup regressions, plus exact interruption and partial-thread-start
  ownership regressions.
- Replaced a timing-flaky real-sleep process test with deterministic fake-clock
  evidence.
- Added primary Python subprocess/array/tracemalloc research and narrow residuals
  in `docs/939-popen-deadline-sparse-hotpaths.md`.

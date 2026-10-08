# Revision 0968 changelog

## Product repair

- Repaired repeated occurrence selection so each invocation advances from the
  newest selected occurrence instead of repeatedly targeting the second match.
- Made occurrence continuation active-buffer-local and derived from cursor IDs
  plus live selections; removed hidden global last-match state.
- Made `SkipMultiCursor` move only the newest matching selection while preserving
  earlier choices and the primary designation.
- Made exhaustion truthful: no state change means the action returns false.
- Replaced the two-pass select-then-insert path that doubled text and newlines.
- Rebased every cursor and retained anchor after multi-location insert, replace,
  paste, delete, indent, and unindent operations.

## Shared edit transaction

- Added `simultaneous_edits.py`, a pure immutable-source planner with exact
  duplicate coalescing, overlap refusal, owner endpoints, and right-affinity
  position mapping.
- Routed text/newline/tab/paste/backspace/delete/cut, indentation, query replace,
  and range/selection hostcalls through the shared geometry.
- Preserved VM arguments and all editor state when hostcall planning fails.
- Added a single-cursor direct splice fast path so ordinary typing does not
  rebuild the whole document.
- Refactored `Buffer.replace_range()` into one mutation and normalized only CRLF
  and CR at the buffer boundary; Unicode line separators remain data.

## Macro and undo transaction

- Made one successful macro playback invocation one aggregate undo/redo row,
  including repeated and multi-buffer playback.
- Suppressed per-step undo snapshots for known built-in action-only macros.
- Preserved exact history semantics for commands, extension actions, and macros
  containing Undo/Redo, then collapsed successful temporary history.
- Kept navigation-only macros out of undo history and preserved existing redo.
- Removed retained discarded undo closures and transient action input from
  aggregate transaction callbacks.
- Kept aggregate undo authority bound to the playback caller.
- Reused compact version-plus-cursor snapshots inside suppressed edit boundaries
  and replace-all operations.
- Removed a duplicate selected-range read from the one-cursor splice and made
  compound transaction target formatting linear and precomputed.

## Evidence and documentation

- Added complete select-next -> select-next -> skip -> visible screen -> edit ->
  undo/redo journeys, simultaneous-edit planner tests, macro transaction tests,
  overlap/argument-preservation tests, and deterministic reference fuzzing.
- Updated the multicursor, macro, hostcall, query-replace, and fileformat contracts.
- Collapsed two competing draft 924 notes and duplicate D22 decisions into one canonical contract, and regenerated the installed effect/resource help page from its live owner.
- Added `docs/924-multicursor-simultaneous-edit-macro-transaction.md` with the
  failure analysis, primary-source research, boundaries, and next speculation.

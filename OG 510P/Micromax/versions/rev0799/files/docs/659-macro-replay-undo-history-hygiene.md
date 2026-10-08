# Rev659 / rev718 — macro replay undo-history hygiene

Rev718 is a small trust follow-up to rev716/rev717's macro replay cleanup.
Failed playback already rolled visible buffer text, cursors, selections, the
active buffer, and command-history noise back to the pre-replay state, but the
rollback path still replaced `EditorBuffer` objects with fresh instances and
left whatever undo entries were recorded during the aborted replay on the live
undo stack.

That made the recovery look right until the user pressed `undo` or `redo`.
Older undo entries close over the original `EditorBuffer` object, so replacing
that object during rollback could leave the undo stack apparently populated but
pointing at stale, detached buffers. Aborted replay edits could also consume the
next undo step or clear redo history even though the macro never completed.

The fix keeps the same all-or-nothing replay surface while making the history
rollback boring and inspectable:

- `UndoManager.snapshot()` and `UndoManager.restore(...)` capture and restore
  undo/redo stack membership plus suppression depth.
- `MacroReplaySnapshot` now carries that undo snapshot.
- `MacroReplayBufferSnapshot` keeps a reference to the pre-existing
  `EditorBuffer`, and rollback mutates that object back into its saved state
  instead of replacing it.
- Failed replay still reports `macro: aborted at step N: ...`, but the visible
  undo/redo lanes are exactly what they were before playback started.

Focused tests pin both sides of the seam: an older undo entry still operates on
the live buffer after an aborted macro, and pre-existing redo history remains
available after rollback.

# Rev0779 — Transient input scratch and direct-edit undo boundary

## Audit finding

Macro replay input was isolated earlier, but the editor-wide `editor.input` scratchpad itself remained shared process state.  Script-originated and deferred callbacks could call `ed.input-set` / `ed.input-clear`, return successfully, and leave values behind for a later user/editor action.  One practical shape was a script-created keybinding or timer writing `input["text"]`; a later trusted `InsertText` action would then consume that stale value.

The adjacent direct-edit surface also had an integrity wrinkle: `ed.set-text` respected the readonly/protected-buffer guard, but it replaced buffer text without recording an undo step.  Other direct edit hostcalls already use editor undo machinery.

## Change

New seam:

`src/micromax_editor/transient_state.py`

It owns tiny snapshot/restore helpers for the action-input scratch dict.  `Editor.script_context(...)` now snapshots `editor.input` on entry and restores it on exit.  Because deferred script/plugin keybindings, timers, hooks, macros, and command callbacks re-enter script context, their scratch writes are now contained to the callback execution window.

`src/micromax_editor/edit_boundary.py` also now exposes `set_buffer_text_undoably(...)`.  `ed.set-text` uses it after the existing readonly/protected-buffer preflight, so direct whole-buffer replacement is one undoable operation.

## Concrete fixes

- `ed.input-set` and `ed.input-clear` inside script context no longer poison later trusted actions.
- Script-created keybindings and timers cannot leave stale action input behind after their callback returns.
- Nested script action dispatch can still use temporary input while the script callback is active.
- `ed.set-text` records a single undo/redo step for the replacement.
- Readonly denial still happens before operation arguments are consumed.

## Validation

Focused regressions in `tests/test_editor_transient_state.py` cover script-context scratch restoration, nested `ed.run` behavior, deferred keybinding/timer scratch restoration, and undo/redo for `ed.set-text`.

Additional focused runs covered macro authority, readonly hostcall denial, runtime-registration policy, and the bounded default doctor lane.

## Remaining risk

The input scratchpad remains intentionally mutable for trusted interactive/editor code.  This boundary isolates lower-authority `script_context` execution; it is not meant to make every direct Python object mutation transactional.  The snapshot is shallow because current action inputs are scalar/portable values.  If future inputs become mutable containers that are edited in place, this seam should grow a deep-copy or value-normalization rule.

# Rev798 — undo/redo authority boundary

## Audit finding

Undo/redo is not just an editing convenience; it is executable recovery state.
Before this revision, lower-authority script-origin code could call `undo` or
`redo` through the command/action surface and replay the top user/trusted entry.
That meant a script that had no filesystem write authority and no dirty-buffer
discard authority could still erase or reapply user edits by consuming trusted
undo history.

The failure mode was concrete: create a trusted edit, enter `script_context()`,
and run `undo`. The edit disappeared and the trusted undo entry moved to redo.
The same problem existed in the opposite direction for trusted redo entries.

## Change

Undo entries now carry the same runtime authority shape used for marks,
selection/jump/history registers, macros, keybindings, timers, hooks, and
commands.

Changed surfaces:

- `micromax_editor.undo.Edit.authority`
- `Editor._record_undo_snapshot(...)`
- `Editor._record_buffer_transaction_snapshot(...)`
- `Editor.undo_feedback()`
- `Editor.redo_feedback()`
- capability registry entry `ed.undo-redo`
- option `cap.undo-redo`

Trusted/interactive callers keep normal undo/redo behavior. Script-origin
callers can replay same-origin undo/redo entries, but cannot replay trusted/user
entries or another script's entries unless trusted code explicitly enables the
unsafe `cap.undo-redo` override.

## Why this is separate from `cap.history-clear`

`cap.history-clear` is cleanup/prune authority for evidence registers. Undo/redo
is stronger: it executes stored callbacks that mutate buffer state. Keeping
`cap.undo-redo` separate avoids turning broad history cleanup permission into an
implicit edit-replay permission.

## Regression coverage

Added `tests/test_editor_undo_authority.py` covering:

- script-origin `undo` cannot consume a trusted user edit;
- script-origin `redo` cannot replay a trusted undone edit;
- a script can undo/redo its own edit;
- an independent script cannot undo another script's edit;
- trusted `cap.undo-redo` enables intentional broad replay.

`tests/test_editor_capabilities_registry.py` now also checks feature
advertisement for `ed.undo-redo`.

## Remaining risk

Direct Python access to `ed.undo.undo()` is intentionally still a trusted host
API, not a script-visible Micromax hostcall. Future work should keep it that way
or add equivalent guard helpers if a public `ed.undo` / `ed.redo` hostcall is
introduced.

# Rev785 — `ed.with-undo` marks transaction and scope/timer hostcall preflight

This turn stayed on the rev784 risk lane: runtime hostcalls that look transactional or scoped must not leave hidden editor state behind, and malformed or denied control hostcalls should not consume the evidence a script needs to diagnose recovery.

## What was risky

Rev784 made `ed.with-undo` an all-open-buffer transaction, but the snapshot still omitted global mark state. That meant a failing quotation could move or add named marks and then roll text/cursor state back while the marks stayed mutated. A successful quotation had the same blind spot in the undo/redo entry: text edits could undo, but marks created or retargeted inside the group would not undo with the group.

This is not as catastrophic as a failed save, but it is the same trust-class bug: an operation named as a transaction had a hidden side effect outside its rollback boundary.

The adjacent bridge audit found a second class of smaller but still annoying failures: scope/control hostcalls such as `ed.after`, `ed.cancel-timer`, `ed.run`, `ed.command`, `ed.with-messages`, `ed.capture-messages`, `ed.with-viewport`, and `ed.with-cursorstate` still used the VM's legacy `pop_*` helpers in some paths. Those helpers consume before type-checking, so malformed calls could erase the bad operand or quotation before raising. `ed.cancel-timer` also consumed the timer id before a script-policy denial.

## What changed

`src/micromax_editor/editor.py`

- `MacroReplaySnapshot` now includes a copied global marks map.
- The same snapshot now includes `_next_cursor_id`, so failed/replayed transactions restore the cursor-id allocator witness as well as per-buffer cursor ids.
- `_macro_replay_snapshot()` copies marks as `(buffer, Cursor)` pairs.
- `_restore_macro_replay_snapshot()` restores only marks whose target buffer exists in the restored topology.
- `ed.with-undo`, macro replay, and cross-buffer transaction undo/redo now share that stronger snapshot.

`src/micromax_editor/micromax_bridge.py`

- `ed.after` now validates both `(ms q)` before consuming either operand.
- `ed.cancel-timer` now checks runtime-policy authority before removing the timer id from the VM stack.
- `ed.run`, `ed.press-key`, `ed.command`, `ed.command-edit`, `ed.topic-prompt`, and `ed.binding-prompt` now preflight string operands before consuming them.
- `ed.with-viewport`, `ed.with-messages`, `ed.capture-messages`, and `ed.with-cursorstate` now preflight quotation operands before consuming them.
- `ed.highlight` now uses the existing two-int preflight shape instead of raw VM pops.

## Regression coverage

`tests/test_editor_with_undo_transaction.py`

- failing `ed.with-undo` quotations roll back mark retargeting and newly created marks;
- successful `ed.with-undo` quotations record mark changes in the single undo/redo step.

`tests/test_editor_hostcall_boundary.py`

- malformed control hostcall operands preserve the stack;
- malformed scope quotation operands preserve the stack;
- malformed timer schedule/cancel operands preserve the stack and do not create timers.

`tests/test_runtime_registration_policy.py`

- script attempts to cancel a trusted timer still fail, and the denied timer id remains on the VM stack.

## Remaining risk

Many lower-risk read-only/detail-row bridge hostcalls still use raw `vm.pop_*`. That is not the same data-loss or authority bug as mutation/scope/control hostcalls, but the bridge should eventually use the peek-then-commit helper family consistently.

`ed.with-undo` is still an editor-visible transaction, not a full host/world transaction. It does not attempt to roll back filesystem writes, plugin loads, external clipboard actions, or arbitrary host effects performed inside the quotation. That boundary should stay explicit in docs and host API naming.

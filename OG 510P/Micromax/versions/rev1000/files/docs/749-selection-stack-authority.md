# Rev792 selection recovery stack authority

Rev792 continues the runtime-state audit after the mark and help-doc containment work.  The concrete target is the saved-selection recovery stack behind `ed.push-selections`, `ed.pop-selections`, `ed.clear-saved-selections`, and the implicit saved-selection clear performed by `ed.set-selections`.

## Failure mode

The selection recovery stack is not undo history; it is a small long-lived editor register that helps a user recover from accidental cursor/selection loss.  Before this revision, script-originated code could:

- pop a trusted/user recovery snapshot and consume it;
- clear the entire saved-selection stack;
- call `ed.set-selections`, which changed cursor state and then cleared the recovery stack as a side effect;
- do all of the above without ownership/provenance checks.

That made lower-authority script code able to erase user/editor recovery evidence even though recent revisions had already protected commands, keybindings, timers, hooks, marks, plugin callback state, and file boundaries.

## Change

`EditorBuffer` now carries a parallel `sel_stack_authority` sidecar for `sel_stack`.  Each saved selection snapshot records the runtime authority active when it was pushed:

- trusted/interactive pushes get trusted authority;
- script pushes get the current script-origin token;
- plugin/script pushes inherit the same runtime authority shape used by other deferred registrations.

The editor normalizes the sidecar for legacy/missing rows by defaulting them to trusted authority.  `pop_selections()` and `clear_saved_selections()` now preflight the saved rows through the shared runtime mutation policy before removing anything.

`ed.set-selections` also changed its ordering: it now preflights the destructive saved-selection clear before mutating live cursor/selection state or consuming the VM-stack operand.  A denied script call leaves the cursor state, the recovery stack, and the caller's operand intact.

## Transaction coverage

The macro/hostcall transaction snapshot now preserves `sel_stack_authority` along with `sel_stack`, so failed `ed.with-undo`/transaction-style restores do not leave selection snapshots with stale or defaulted provenance.

## Tests

New regression file:

- `tests/test_editor_selection_stack_authority.py`

It covers:

- scripts cannot pop trusted saved selections;
- scripts can pop their own saved selections;
- independent scripts cannot clear one another's saved selections;
- `ed.set-selections` denial preserves cursor state, stack, and operand;
- transaction restore preserves the selection-stack authority sidecar.

## Remaining risk

The same audit pattern should still be applied to jump history, docs help history, recent-file MRU destructive operations, and message-log destructive hostcalls.  Those registers are less directly dangerous than disk writes, but they are still long-lived editor memory and can affect later user trust/recovery loops.

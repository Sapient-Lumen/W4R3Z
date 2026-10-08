# Rev790 — mark authority and plugin rollback coverage

Rev0790 continues the delayed-authority audit from the bridge/runtime work.  The next concrete state surface was the named-mark register: marks are small, but they are long-lived navigation state, they are script-visible through `ed.mark-set`, and they participate in transactions, macro replay, save-as rollback, and plugin cleanup.  Before this revision, a lower-authority script could overwrite a trusted/user mark and then leave that poisoned jump target behind for a later user action.

## What was risky

`ed.mark-set` was a direct mutation of `Editor.marks`.  Recent revisions had added provenance checks for commands, keybindings, hooks, timers, macros, prompts, active keymodes, and several file-operation surfaces, but marks were still only a `dict[str, (buffer, cursor)]`.  That left three holes:

- a script-origin hostcall could retarget a user/trusted mark;
- independent script origins could retarget each other's marks;
- failed plugin callback/load/reload paths rolled back commands, keybindings, hooks, timers, and VM dictionary state, but not marks created during the failed callback.

That is not the same severity as a disk overwrite, but it is the same *shape* as the runtime-registry bugs fixed in rev0778-rev0777: a lower-authority callback can mutate durable editor state now and rely on a later trusted navigation action to experience the surprise.

## What changed

`src/micromax_editor/editor.py`

- Adds `_mark_authority`, a sidecar authority map for named marks.
- `Editor.mark_set(...)` now applies the same runtime mutation policy used for commands/keys/hooks/timers when the current caller is inside `script_context()`.
- Trusted/user calls can still overwrite any mark.
- Lower-authority scripts can create marks and retarget their own marks.
- Independent script origins cannot retarget each other's marks.
- Plugin-origin marks carry plugin root/generation/group provenance.
- Idempotent lower-authority repeats of an existing trusted mark are treated as no-ops rather than downgrading ownership.
- Buffer close, bulk close, save-as rollback, macro replay rollback, and `ed.with-undo` snapshots now keep mark authority aligned with visible marks.
- Adds `remove_mark_group(...)` and `retag_mark_group(...)` so plugin unload/reload cleanup can include marks.

`src/micromax_editor/micromax_bridge.py`

- `ed.mark-set` now peeks its mark-name operand, calls the checked editor mutation path, and only consumes the operand after the mutation is accepted.  A denied mark overwrite leaves the requested mark name on the VM stack as failure evidence.

`src/micromax_editor/command_dispatcher.py`

- `mark NAME` now reports policy denials as normal command failures instead of letting `PermissionError` escape the command dispatcher.

`src/micromax_editor/plugin_runtime.py`

- Runtime registration snapshots now include marks and mark authority.
- Failed plugin callback/load/reload transactions restore marks along with commands, keybindings, hooks, timers, and VM dictionary state.
- Plugin runtime group cleanup removes plugin-owned marks.
- Staged plugin reload retags staged marks when a replacement is promoted to the stable plugin group.

`tests/test_editor_mark_authority.py`

- Proves script-origin `ed.mark-set` cannot overwrite a trusted mark and preserves the name operand on denial.
- Proves idempotent repeats do not downgrade trusted mark ownership.
- Proves independent script origins cannot retarget each other's marks, while the owning script can.
- Proves failing `ed.with-undo` quotations restore the mark-authority sidecar.
- Proves plugin runtime registration snapshots restore marks after failed plugin callback-style mutations.
- Proves plugin runtime group retag/cleanup covers marks.

## Remaining risk

Marks now have provenance, but the jump list and recent-file MRU are still mostly session-local state without the same ownership model.  They are lower risk than commands/keys/hooks/timers because they are not arbitrary callbacks and do not execute code, but future work should still audit destructive script-visible history operations such as clearing recent files, clearing jumps, clearing saved selections, and popping messages.

`ed.with-undo` remains an editor-visible transaction rather than a full host/world transaction.  It now keeps mark authority coherent with mark values, but it still does not roll back external host effects performed inside a quotation.

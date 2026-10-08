# Rev789 — mutable value snapshots for rollback boundaries

Rev0789 follows through on the rev0788 stack-rollback claim.  The previous bridge/scoped-helper work restored the VM stack list after a failing protected quotation, but the restore was shallow.  A quotation could mutate a caller-owned list or map value in place, fail, and the restored stack would still point at the mutated object.

## Audit finding

Micromax exposes portable mutable host values through `list`, `push`, `set-nth`, `map`, `m!`, `m-del`, and related words.  Several safety boundaries were using shallow snapshots:

- core `catch` saved `list(vm.stack)`;
- editor scoped hostcalls saved `list(vm.stack)`;
- plugin execution/callback rollback saved stack containers by reference;
- `Editor.script_context()` restored the `Editor.input` mapping membership, but not nested mutable values returned by `ed.input-get`.

That meant the boundary restored the stack shape but not the actual caller-visible value state.  A failing helper could run `push` against a list that was already on the caller stack, or a script could fetch `Editor.input["payload"]`, mutate the returned list, and then exit with the supposedly restored scratchpad still poisoned.

## What changed

New module:

`src/micromax/value_snapshot.py`

It snapshots only Micromax's portable mutable containers: `list` and `dict`, recursively, with memoization for shared or self-referential containers.  Runtime identity objects such as words, quotations, cells, cursors, and host handles remain identity values.

Changed users:

- `src/micromax/core.py` uses `snapshot_stack(...)` for `catch` failure restoration.
- `src/micromax_editor/hostcall_transactions.py` uses `snapshot_stack(...)` for scoped hostcall stack rollback.
- `src/micromax_editor/plugin_runtime.py` uses value snapshots for data stack, return stack, and locals-frame values in plugin execution/callback rollback.
- `src/micromax_editor/transient_state.py` snapshots `Editor.input` nested portable containers, not just key membership.

## Concrete fixes

- A failing `catch` quotation can no longer mutate a caller-owned list/map and leave the mutation behind after `catch` restores the stack.
- Failing scoped editor helpers such as `ed.with-messages`, `ed.with-buffer`, `ed.with-cursorstate`, and `ed.with-undo` now restore mutable list/map operands as well as stack depth/order.
- Script/deferred callbacks can no longer poison nested list/map values stored in `Editor.input` and rely on shallow restoration to preserve the mutation for later trusted actions.
- Failed plugin callbacks and lifecycle execution use the same portable-container snapshot discipline for stack-like VM state.

## Remaining risk

This is still an application-level value snapshot, not a deep clone of arbitrary host objects.  It deliberately copies only Micromax's portable container values.  If future hostcalls put mutable custom objects on the stack and expose mutators for them, those objects will need their own explicit transaction rule.

`catch` now has a stronger observable contract for portable containers than before.  That matches the documentation phrase “restores the stack,” but ports should copy the same `list`/`dict` semantics if they want byte-for-byte parity with the Python host.

## Validation

Focused validation included:

- `tests/test_editor_transient_state.py::test_script_context_restores_mutable_action_input_values`
- `tests/test_editor_hostcall_transactions.py::test_scope_transaction_failure_restores_mutable_stack_values`
- `tests/test_vm_rev11.py::test_catch_restores_mutable_stack_values_on_throw`
- `tests/test_plugin_containment_and_caps.py::test_failed_plugin_command_callback_restores_mutable_stack_values`
- broader transient-state, hostcall-transaction, VM catch/smoke, and plugin containment tests.

Additional handoff evidence: `mxtest --plan --chunks 8 --strategy segment` collected 1913 tests into chunks `240, 239, 239, 239, 239, 239, 239, 239`.  A default `mxdoctor` attempt hit cloudtainer SIGTERM behavior, so this revision does not claim a fresh doctor or full-suite aggregate pass.

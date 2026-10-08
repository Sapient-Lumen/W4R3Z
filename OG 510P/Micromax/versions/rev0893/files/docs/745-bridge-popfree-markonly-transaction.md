# Rev788 — bridge pop-free stack snapshots and mark-only transactions

Rev0788 finishes the runtime transaction lane that was already visible in the rev0787 handoff. The priority was not another registry pass: it was making the host/editor boundary behave like an actual boundary when transactions fail, and making `ed.with-undo` honest for mark-only changes.

## Audit finding

The rev0787 mark snapshot landed the right state into `MacroReplaySnapshot`, but the transaction change predicate still only compared active buffer identity, MRU order, and buffer snapshots. A quotation that only created or retargeted a mark could therefore complete successfully without recording an undo entry, even though the snapshot was now capable of restoring marks. That made the promised mark transaction incomplete for the simplest mark-only case.

The bridge audit also found that “scoped” helpers restored editor-visible state but not the VM data stack. A failing quotation inside `ed.with-buffer`, `ed.with-viewport`, `ed.with-messages`, `ed.capture-messages`, `ed.with-cursorstate`, or `ed.with-undo` could push junk and then fail. Worse, it could consume the caller's pre-existing operands with `drop` and still leave the caller to recover from the exception with a damaged stack.

The remaining editor bridge hostcalls had already been migrating away from the VM's consuming `pop_*` helpers. Rev0788 completes that bridge-side direction for the editor host boundary: bridge calls should validate type/policy first, then commit stack changes.

## What changed

`src/micromax_editor/editor.py`

- `_buffer_transaction_changed(...)` now compares global mark state as well as open-buffer state.
- It also compares `_next_cursor_id`, keeping the change predicate aligned with the transaction snapshot.
- The undo target label reports `marks` for mark-only changes and `N targets` when both buffers and marks changed.

`src/micromax_editor/hostcall_transactions.py`

- Adds `capture_vm_stack(...)` and `restore_vm_stack_snapshot(...)`.
- Keeps the older depth-trim helper as compatibility glue, but scoped hostcalls now use full stack snapshots so a failing quotation cannot consume caller operands before raising.

`src/micromax_editor/micromax_bridge.py`

- All remaining editor bridge hostcalls have been migrated away from raw `vm.pop_*`, `vm.pop()`, and `vm.stack.pop` usage.
- Multi-operand int hostcalls use local peek-then-delete helpers so every operand is validated before any are removed.
- Scope helpers restore the VM stack snapshot on quotation failure after their own hostcall operands have been consumed.
- Read-only/detail-row hostcalls now share the same typed stack-evidence behavior as the higher-risk mutation/scope hostcalls.

`tests/test_editor_hostcall_boundary.py`

- Static bridge guard proves `micromax_bridge.py` has no raw consuming VM pop helpers.
- Malformed display/model/query/prompt/input/scope/timer/viewport cases prove operands are preserved.

`tests/test_editor_hostcall_transactions.py`

- Failing scoped helper quotations now prove the original VM stack snapshot is restored, even when the quotation executes `drop` before failing.

`tests/test_editor_with_undo_transaction.py`

- Adds a mark-only `ed.with-undo` regression. Creating a mark inside the group now records one undo step; undo removes the mark and redo restores it.

## Remaining risk

The core Micromax VM and standard-library primitives still use normal Forth-style consuming stack operations. That is correct for the language core. The stricter rule in this revision applies to the editor bridge because bridge calls cross into host/editor authority and need better diagnostics on malformed direct calls.

`ed.with-undo` is still an editor-visible transaction, not a host/world transaction. It rolls back editor buffers, marks, cursor/id evidence, VM-stack state for failed scope quotations, and undo membership, but it does not roll back filesystem writes, plugin loads, shell commands, external clipboard operations, or URL dispatch performed by a quotation.

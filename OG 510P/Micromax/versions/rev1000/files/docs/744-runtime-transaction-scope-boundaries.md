# 744 Runtime transaction and scope-control hostcall boundaries

Rev0787 packages the transaction-boundary work that was already partly staged in this cloudtainer plus the follow-up cursorstate/message/timer audit from this turn. The goal is one coherent runtime repair: helpers named as transactions or temporary scopes must not leave hidden editor state behind, and failed control hostcalls should not erase the evidence needed to diagnose recovery.

## Audit finding

The rev0784 `ed.with-undo` fix made text/cursor state all-buffer transactional, but the editor-level snapshot still omitted global named marks and the cursor-id allocator. That meant a failing grouped quotation could roll text back while leaving marks moved or newly created. A successful grouped quotation also omitted mark changes from the single undo/redo step.

A sibling helper, `ed.with-cursorstate`, had a separate cross-buffer leak. It snapshotted only the active buffer at entry. A helper quotation could switch to another buffer, move that buffer's cursor, and return or fail while leaving the user in the wrong active buffer or leaving another buffer's cursor moved.

The adjacent control/scope hostcalls also had stack-boundary debt. Timer scheduling/cancellation and message/cursor scope helpers were still close to legacy pop-before-type-check behavior in places. On malformed calls or script-policy denials, operands such as quotations, timer ids, or command strings could disappear from the VM stack before the failure was visible.

## Change

`src/micromax_editor/editor.py`

- Macro/transaction snapshots now include global mark state.
- Macro/transaction snapshots now include `_next_cursor_id` so rollback/redo restores cursor-id allocation evidence, not just per-buffer ids.
- `ed.with-undo`, macro replay rollback, and cross-buffer transaction undo/redo share the stronger snapshot.

`src/micromax_editor/hostcall_transactions.py`

- New small seam for editor-visible hostcall transactions.
- Captures/restores all-open-buffer cursor/selection state, active buffer identity, MRU order, selection stack, jump stack, and message-log state without touching buffer text.

`src/micromax_editor/micromax_bridge.py`

- `ed.with-cursorstate` now restores active buffer identity and cursor/selection state for every buffer that was open at entry.
- New buffers created by a helper quotation are preserved, while captured buffers do not keep helper cursor debris.
- `ed.with-messages` and `ed.capture-messages` use the shared message snapshot helper.
- `ed.after` and `ed.cancel-timer` use peek-then-commit argument handling.
- Command-like script entry hostcalls consume string operands only after the requested operation returns.

`tools/mxdoctor.py`

- The bounded doctor risk lane includes the new hostcall transaction regression file.

## Concrete guarantees

- Failing `ed.with-undo` quotations restore named marks as well as open buffer text/cursor state.
- Successful `ed.with-undo` quotations record mark creation/retargeting in the same undo/redo step as buffer changes.
- Macro/transaction rollback restores the editor cursor-id allocator witness.
- `ed.with-cursorstate` restores active buffer identity after cross-buffer helper quotations.
- `ed.with-cursorstate` restores cursor/selection state for every buffer open at entry, on success and failure.
- Malformed transaction/timer hostcalls preserve their original VM operands.
- Script-denied `ed.cancel-timer` calls preserve the timer id and leave the trusted timer scheduled.

## Validation evidence

Focused validation passed for the new cursorstate/message/timer transaction tests, existing hostcall-boundary tests, cursor/state argument-boundary tests, with-undo transaction tests, timer/highlight tests, runtime-registration policy tests, prompt completion, and Micromax command integration. The staged mark transaction regressions are present in `tests/test_editor_with_undo_transaction.py` and the scope/timer evidence regressions remain covered by the existing hostcall-boundary/runtime policy tests.

A full-suite aggregate pass is still not claimed. Full evidence should come from a complete chunked `mxtest` manifest.

## Remaining risk

These are editor-visible transactions, not whole-host transactions. They intentionally do not roll back filesystem writes, plugin loads, external clipboard effects, URL dispatch, or arbitrary host effects performed inside a quotation. Many lower-risk read-only/detail-row bridge hostcalls also still use legacy raw pops and should continue migrating opportunistically.

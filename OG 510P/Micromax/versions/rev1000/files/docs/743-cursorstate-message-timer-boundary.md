# 743 Cursorstate, message, and timer hostcall transaction boundary

Rev0786 continues the hostcall-boundary audit from rev0783/rev0784, but targets a more concrete transactional bug rather than widening the registry trail.

## Audit finding

`ed.with-cursorstate` claimed to behave like a save/restore cursor helper, but it only snapshotted the active buffer at entry. A quotation could switch to another buffer, move that buffer's cursor, and return. The original active buffer's cursor was restored, but the active buffer could remain changed and the second buffer's cursor/selection state stayed mutated. The failure path had the same problem: a helper quotation that switched buffers, moved a cursor, and then failed left cross-buffer cursor debris behind.

That was lower stakes than text-loss, but still trust-relevant because these helpers are the building blocks for scripts, prompt helpers, and plugin commands. A helper advertised as temporary state should not permanently move the user's active buffer or another buffer's cursor.

The adjacent message and timer hostcalls had a smaller but related problem: they still mixed raw stack pops or ad-hoc save/restore code into the bridge. That made malformed or denied calls consume evidence in some cases and made future transaction fixes likely to be duplicated inside the monolithic bridge.

## Change

New module:

`src/micromax_editor/hostcall_transactions.py`

It owns small editor-visible transaction snapshots for:

- all-open-buffer cursor/selection/navigation state;
- active-buffer identity and MRU order;
- message-log state.

`ed.with-cursorstate` now captures cursor/selection state for every currently open buffer, restores active buffer identity after the quotation, and restores the captured cursor/selection/jump-selection state even when the quotation fails. New buffers created during the quotation are preserved, but captured buffers no longer keep helper cursor debris.

`ed.with-messages` and `ed.capture-messages` now use the shared message snapshot helper instead of local list-copy logic.

`ed.after` and `ed.cancel-timer` now use peek-then-commit stack semantics. Bad timer arguments leave operands visible, and a script denied from cancelling a trusted timer keeps the timer id on the VM stack.

Command-like script entry hostcalls (`ed.run`, `ed.press-key`, `ed.command`, and prompt-opening helpers) now validate the string argument first and consume it only after the requested operation returns. If execution raises, the initiating action/key/command/prompt string remains visible as failure evidence.

## Guarantees

- `ed.with-cursorstate` restores the active buffer after cross-buffer helper quotations.
- `ed.with-cursorstate` restores cursor/selection state for every buffer that was open when the helper started.
- A failing cross-buffer `ed.with-cursorstate` quotation no longer leaves another buffer's cursor moved.
- Malformed `ed.with-cursorstate`, `ed.with-messages`, and `ed.capture-messages` calls preserve the non-quotation operand.
- Malformed `ed.after` calls preserve both delay and quotation operands.
- Script-denied `ed.cancel-timer` calls preserve the timer id and leave the trusted timer scheduled.
- Command-like script entry hostcalls consume their string only after the requested operation returns.

## Validation evidence

Focused validation passed for the new transaction tests, existing hostcall-boundary tests, cursor/state argument-boundary tests, with-undo transaction tests, timer/highlight tests, runtime-registration policy tests, prompt completion, and Micromax command integration. The bounded default doctor now includes `tests/test_editor_hostcall_transactions.py`.

A full-suite aggregate pass is still not claimed. Full evidence should still come from a complete chunked `mxtest` manifest.

## Remaining risk

The bridge still contains many read-only/introspection hostcalls with legacy raw pop helpers. Most are lower risk because they do not mutate editor state or long-lived registries, but continued migration to shared peek helpers will make direct hostcall failures more inspectable and reduce one-off bridge code.

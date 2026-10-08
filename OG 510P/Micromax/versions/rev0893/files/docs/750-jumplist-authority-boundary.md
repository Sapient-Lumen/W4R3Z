# Rev793 jumplist authority boundary

Rev793 continues the destructive-register audit called out in rev792.  The target is the per-buffer jumplist behind `PushJump`, `jumpback`, `jumpforward`, `jumppick`, `jumps`, and the hostcalls `ed.push-jump`, `ed.jump-back`, `ed.jump-forward`, and `ed.clear-jumps`.

## Failure mode

The jumplist is not undo history, but it is still long-lived recovery state.  Before this line, a script-origin callback could use that register in ways that affected later user trust:

- clear a trusted/user jumplist with `ed.clear-jumps`;
- push a new row while the user was sitting in the middle of trusted history, causing the forward tail to be discarded;
- fill the bounded list and then push again, evicting the oldest trusted row;
- walk `jumpback` / `jumpforward` through trusted rows and leave the current jump slot and cursor state changed.

Those are small operations compared with disk writes, but they are exactly the kind of recovery-register mutation that becomes hard to diagnose later: the user asks to go back and the trail has silently changed.

## Change

`EditorBuffer` now carries `jump_list_authority` beside `jump_list`.  Missing legacy rows normalize to trusted authority, matching the safer rule used for selection recovery snapshots: old editor/user state must not become script-owned merely because a new sidecar was introduced.

The editor now preflights lower-authority mutation of jump rows through the shared runtime mutation policy:

- `clear_jumps()` checks every row before clearing;
- `push_jump()` checks the forward tail before browser-style truncation;
- `push_jump()` checks bounded-history eviction before appending a new row, so a denied script push cannot leave a transient extra row behind;
- `jump_back()`, `jump_forward()`, and `jump_to_index()` check both the current and target rows before mutating the current jump slot or restoring cursor state.

Scripts can still create, clear, and traverse their own jump rows.  Independent script origins cannot mutate each other's rows, and trusted interactive/editor rows remain protected.

## Transaction coverage

Macro replay and hostcall transaction snapshots now preserve `jump_list_authority` along with the visible jump rows and `jump_index`, so rollback cannot launder script-owned rows into trusted rows or lose the sidecar after a failed grouped operation.

## Tests

New focused file:

- `tests/test_editor_jump_history_authority.py`

It covers trusted clear denial, same-origin clear/traversal success, independent-origin denial, trusted forward-tail truncation denial, trusted navigation denial, rollback preservation, and the bounded-list partial-mutation guard.

## Remaining risk

The same destructive-register audit still needs to cover recent-file clearing, help navigation history, and message-log destructive hostcalls.  Those surfaces are not the same as filesystem authority, but they can still erase orientation/debugging evidence that a user depends on after an automated or scripted action.

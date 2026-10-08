# Rev799 clipboard register authority

Rev799 continues the recovery/register audit on the internal clipboard.  The clipboard is not just a transient UI convenience: scripts can read it through hostcalls, paste actions can consume it later, and failed deferred callbacks can leave it changed long after the callback itself reports failure.

## Failure mode

Before this revision, lower-authority script code could read or overwrite the trusted/user internal clipboard through `ed.clipboard`, `ed.clipboard-items`, `ed.set-clipboard`, or `ed.set-clipboard-items`.  Script-triggered Paste could also consume a trusted internal clipboard row even when system-clipboard import was blocked.  A failed plugin callback could similarly leave a partially changed clipboard register behind while other runtime registries rolled back.

That was inconsistent with the protected-register model already applied to marks, selections, jumps, recent rows, help/message history, prompt history, and undo/redo: long-lived editor state should either belong to the caller's runtime authority or require an explicit capability override.

## Change

`Editor.clipboard_authority` now records the runtime authority that last materially changed the internal clipboard.  Script-context reads and writes use the same-origin rule:

- empty clipboard reads/writes remain harmless;
- same-origin scripts can read/update their own clipboard rows;
- trusted interactive/user code remains unrestricted;
- cross-origin or trusted clipboard reads require `cap.clipboard-read`;
- cross-origin or trusted clipboard writes require `cap.clipboard-write`.

The clipboard hostcalls now preserve denied-operation evidence where practical.  `ed.set-clipboard` and `ed.set-clipboard-items` validate their operands before mutation; if the policy denies the write, the original operand remains on the VM stack.

Paste now obtains the internal clipboard through `clipboard_items_snapshot()`, so a script-triggered Paste cannot silently read trusted internal clipboard text after external/system import is unavailable or blocked.

Failed plugin callback rollback snapshots now include the clipboard register, its authority sidecar, serial, and script-origin export bit.  A callback that changes the clipboard and then fails does not strand the failed value as live editor state.

## Capability wording

`cap.clipboard-read` and `cap.clipboard-write` continue to gate system clipboard import/export.  Rev799 also makes them the explicit override for script-origin access to the internal clipboard register.  This keeps one clipboard capability vocabulary instead of inventing a second pair for the in-process register.

## Validation

Focused regressions cover denied script reads, denied script writes, same-origin script clipboard use, explicit read/write capability overrides, script-triggered Paste denial against trusted internal clipboard, and failed plugin callback rollback of clipboard state.

## Remaining risk

This is editor-level provenance inside a single process, not an OS clipboard sandbox.  Trusted interactive code still has ambient clipboard access by design.  Future direct mutations of `clipboard_items` or `clipboard_kind` should be converted to `set_clipboard_items()`, `append_clipboard_items()`, or a similarly guarded helper.

## Cut/CutLine preflight follow-up

The same audit also found a narrower but dangerous ordering bug in text-cut actions.  `Cut` and `CutLine` are both edit operations and clipboard writes.  If a script tried to cut while the live clipboard belonged to trusted/user authority, the old ordering could delete buffer text first and only then discover that the clipboard write was denied.  `CutLine` had an extra bypass when line-cut accumulation was active: it appended directly to `clipboard_items` instead of going through the guarded clipboard helper.

Rev799 now preflights clipboard-write authority before destructive cut edits.  `Cut` checks the clipboard boundary before deleting the selected text.  `CutLine` checks before deleting any line, and accumulation appends through `Editor.append_clipboard_items(...)`, which updates clipboard provenance and serial state through the same policy path as `set_clipboard_items(...)`.

Additional regressions cover denied script `Cut`, denied script `CutLine`, denied accumulated line-cut append to a trusted clipboard, and successful same-origin script line-cut accumulation.

# Rev807 message-log read authority and register-index catch-up

## Why this was risky

The message log was already protected against destructive script-origin mutation:
script code could not pop or clear trusted/user rows unless a trusted caller had
enabled `cap.history-clear`.  The read side still lagged behind.  A lower-
authority script could call `ed.messages`, `ed.last-message`, `ed.capture-
messages`, or inspect statusline `last_message` and learn trusted recovery
evidence: paths, failed commands, save-conflict details, URL confirmations, or
other user-facing diagnostics.

That made messages unlike the rest of the protected-register family.  Recent
work protected marks, macros, undo/redo, clipboard state, recent rows, prompt
history, active search, and delayed interactions, but message-log reads were
still ambient.

## What changed

New module:

`src/micromax_editor/message_policy.py`

New capability:

- `cap.message-read` / `ed.message-read`

`Editor.visible_messages()` and `Editor.last_visible_message()` now filter
message rows through runtime authority.  Trusted/user callers still see the
normal log.  Script-origin callers see rows they emitted from the same script or
plugin generation; trusted/user rows and other-origin rows are hidden unless a
trusted caller explicitly enables `cap.message-read`.

The guarded read model now applies to:

- `ed.messages`
- `ed.last-message`
- `ed.capture-messages`
- `Editor.status_model()["last_message"]`

Mutation policy did not change: `ed.pop-message` and `ed.clear-messages` still
use the existing per-row mutation boundary, with `cap.history-clear` remaining
the explicit destructive cleanup override.  The new `cap.message-read` is read-
only and does not grant clearing authority.

## Catch-up fixed in this handoff

The linked rev0804 archive already contained later unlinked palette/search
content lines.  Rev807 preserves that work and makes the handoff trail explicit:
rev805 palette MRU authority and rev806 active-search authority remain indexed,
and rev807 records the message-read boundary as the current line instead of
silently rolling back those already-landed files.

## Validation

Focused regression coverage now proves:

- script-origin `ed.messages` hides trusted and other-origin rows;
- script-origin `ed.last-message` returns the newest visible row only;
- statusline `last_message` hides protected rows in script context;
- `ed.capture-messages` cannot launder trusted messages emitted during capture
  into a script-readable return value;
- `cap.message-read` advertises `ed.message-read` and permits protected reads;
- the pre-existing destructive message-log authority tests still pass.

## Remaining risk

This is runtime provenance, not a secrecy boundary against trusted code or a
host process debugger.  The protected-register audit should continue with any
remaining script-visible picker/session registers that have a read side, a
replay side, and delayed user intent.

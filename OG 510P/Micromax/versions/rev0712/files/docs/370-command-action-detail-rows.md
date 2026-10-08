# Rev428: tiny shared command/action detail rows

## What changed

- Added `command_detail_row(NAME)` in the editor core.
- Added `action_detail_row(NAME)` in the editor core.
- Added hostcalls `ed.command-detail-row` and `ed.action-detail-row`.
- Plain `showcmd NAME` now reuses `command_detail_row(NAME)`.
- New plain `showaction NAME` reuses `action_detail_row(NAME)`.
- `help NAME` now reuses those same shared rows for command/action topics instead of formatting them ad hoc.
- Prompt completion now understands `showaction NAME`.

## Why this is worth doing

Micromax already had good *search* for commands and actions: `help`, `topicpick`, `commandpick`, `ed.topic-rows`, and palette rows all made discovery easy. But direct inspection was still asymmetric. Commands had a human-facing `showcmd NAME` path with no matching tiny machine-facing single-row hostcall, and actions had no first-stop direct inspection path at all.

That asymmetry was small, but it mattered for trust and future scripting:

- humans could inspect one command directly, but scripts still had to rescan `ed.cmd-rows`
- humans could discover actions, but not inspect one action directly without using broader search/help surfaces
- help/command formatting for commands/actions still lived in multiple places

Rev428 keeps the fix tiny and inspectable. The host boundary now exposes one direct row per command/action, and the human-facing command/help paths reuse that same row data.

## Row shapes

- `command_detail_row(NAME)` / `ed.command-detail-row` -> `[name doc group|0 [file line col]|0] | 0`
- `action_detail_row(NAME)` / `ed.action-detail-row` -> `[name doc [file line col]|0] | 0`

Those shapes intentionally stay small:

- command rows preserve the exact detail already shown by `showcmd`
- action rows only expose what actions actually own today: name + doc

## Direct user-visible effect

- `showaction InsertText` now works
- `showcmd NAME` and `help NAME` for commands/actions reuse shared detail rows
- missing direct inspection stays explicit: `showaction: no such action: NAME`

## Follow-up seams

- a tiny shared resolved action-spec/provenance row for bindings/macro steps could make command/action inspection line up even better with keymap debugging
- macro runtime state is still split between saved macro inventory and separate recording/playing booleans
- broader search surfaces (`topicpick`, `apropos`) are still richer than tiny grouped/count-aware script snapshots for discovery results

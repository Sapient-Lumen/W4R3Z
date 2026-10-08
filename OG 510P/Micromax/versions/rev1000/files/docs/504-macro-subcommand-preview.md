# Rev562 — `macro list` / `macro status` command-bar previews reuse live macro state

## Why

Micromax already had the right tiny state underneath the broad macro subcommands:

- `macro list` already emitted a count-aware saved-macro inventory after Enter
- `macro status` already emitted the live runtime state for idle / recording / playing plus saved-macro count
- `macro_inventory_rows()` and `macro_status_rows()` already exposed those same tiny registers headlessly

But exact `macro list` / `macro status` completion still fell back to a generic `macro action` placeholder, and canonical `status` was missing from `macro` subcommand completion even though the dispatcher supported it.

## What changed

- added shared `_prompt_macro_command_row(...)`
- exact `macro list` completion now reuses `macro_inventory_rows()`
- exact `macro status` completion now reuses `macro_status_rows()`
- canonical `status` now appears in `macro` subcommand completion
- the rows stay intentionally small:
  - `0 macros`
  - `2 macros · e.g. demo (1 step)`
  - `idle · 2 macros · e.g. demo (1 step)`
  - `recording · demo (1 step) · 0 macros`

## Why this shape

This keeps broad macro inspection aligned with Micromax's existing headless-first automation registers instead of inventing another one-off summary path. `macro list` stays about saved inventory; `macro status` stays about current runtime state plus saved-count context. Together they make the command bar tell the same tiny truth those commands already trust after Enter.

Future humans and LLMs can now see both saved-macro inventory and live macro runtime state before Enter, and they can discover canonical `macro status` from completion without already remembering it.

## Checks

Focused prompt-completion coverage now pins:

- empty `macro list` and `macro status` rows
- `macro` subcommand completion including canonical `status`
- recording-state `macro status` preview
- saved-inventory `macro list` / idle `macro status` previews after `macro stop`

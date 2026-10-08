# Rev565 — truthful macro action subcommand previews

## Why

Micromax already had the important nearby pieces:

- `macro list` / `macro status` already previewed broad macro inventory/runtime truth before Enter
- exact `macro play NAME` / `macro record NAME` rows already reused saved-slot counts and overwrite-vs-new-slot intent
- the dispatcher already accepted `macro rec` / `macro start` aliases plus `macro stop` / `macro cancel` recording-state behavior

But one small seam still lingered at the broad action layer: plain `macro play`, `macro record`, `macro rec`, `macro start`, `macro stop`, and `macro cancel` still collapsed back to a generic `macro action` placeholder, and completion still hid the real `rec` / `start` aliases even though the editor already supported them.

## What changed

- `_prompt_macro_command_row(...)` now reuses `macro_status_rows()` / `macro_inventory_rows()` across the action-side macro subcommands too
- plain `macro play` now previews saved macro inventory before Enter
- plain `macro record` / `macro rec` / `macro start` now preview `default=last` when idle, and switch to a live `stop or cancel first` guard when recording is already active
- plain `macro stop` / `macro cancel` now preview `save macro` / `discard macro` only when recording is actually active, and otherwise stay explicit as `idle · not recording`
- `macro` subcommand completion now also offers the real `rec` / `start` aliases so the prompt surface matches the dispatcher surface

## Examples

- `play  →  0 macros`
- `record  →  idle · default=last · 0 macros`
- `rec  →  idle · default=last · 0 macros`
- `stop  →  idle · not recording`
- `record  →  recording · demo (1 step) · stop or cancel first`
- `stop  →  recording · demo (1 step) · save macro`
- `cancel  →  recording · demo (1 step) · discard macro`
- after save: `play  →  2 macros · e.g. demo (1 step)`

## Tests

Focused prompt-completion coverage now pins:

- idle `play` / `record` / `rec` / `start` / `stop` / `cancel` rows
- alias visibility for `rec` / `start`
- recording-state `play` / `record` / `stop` / `cancel` rows
- saved-inventory follow-up rows after `macro stop`

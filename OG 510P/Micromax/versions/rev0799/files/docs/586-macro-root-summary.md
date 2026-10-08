# Rev645 - plain `macro` root summary

## What changed

Plain `macro` now keeps one tiny truthful macro-state witness visible both
before Enter and after Enter with no subcommand:

- the exact no-arg command-bar row now previews a compact combined summary such as
  `idle · 0 macros`,
  `recording · demo (1 step) · 0 macros`, or
  `idle · 2 macros · e.g. demo (1 step)`
- the raw runtime `macro` path now prints that same summary before
  `usage: macro record|stop|cancel|play|list ...`

## Why this matters

Micromax already knew the live macro runtime state and saved-slot inventory.
Its subcommands were already using that truth, but the umbrella entry point was
still blinder than the paths beneath it.

That was a small trust/flow mismatch:

- before Enter, plain `macro` looked like generic command metadata
- after Enter, plain `macro` jumped straight to syntax
- the one place people naturally type first for automation orientation hid the
  very state Micromax already had

## Implementation notes

- new shared `_macro_root_preview_summary()` combines `macro_status_rows()` and
  `macro_inventory_rows()` into one compact witness
- new `_prompt_macro_root_command_row(...)` reuses that summary for the exact
  no-arg command-bar row
- new `_macro_runtime_root_summary(...)` keeps the runtime no-arg path aligned
  with the command-bar preview
- `c_macro(...)` now emits the summary before its usage hint when called with
  no subcommand

## Tests

Focused coverage pins the root behavior in three states:

- idle with no saved macros
- recording with one in-flight step
- idle again with saved `demo` / `last` inventory after stop

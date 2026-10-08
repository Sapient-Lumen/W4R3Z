# Rev632 — `helphistory` command preview keeps the local docs trail visible

## What changed

Plain `helphistory` now previews the same tiny count-aware docs-history summary
in the command bar that the runtime command already prints after Enter.

The exact no-arg command row no longer falls back to generic command metadata.
Instead it reuses one shared history-summary helper and can now show:

- `helphistory: 0 help target(s)`
- `helphistory: 2 help target(s), [here] softwrap @ 1:0; [back 1] help-browser @ 8:3`
- `helphistory: 2 help target(s), [dormant] help-browser @ 8:3; [forward 1] softwrap @ 1:0`

## Why it matters

This is a tiny trust/flow follow-up in the same docs-browser recovery loop as
`helpback`, `helpforward`, `helpresume`, and `helpprune`. Micromax already knew
exactly what `helphistory` would report after Enter, but the command bar still
hid that live trail behind generic command prose right before execution.

Keeping the prompt row and runtime command on one shared summary helper makes
the docs-history surface easier to trust, easier to scan, and easier for future
LLMs or humans to extend without having to reconcile two slightly different
dialects for the same local state.

## Implementation notes

- added `Editor.help_history_inventory_summary()` as the shared tiny witness
- added `_help_history_inventory_entry_summary(...)` to keep lane tags like
  `[here]`, `[dormant]`, `[back 1]`, and `[back 1 missing]` stable
- wired exact `helphistory` prompt completion through
  `_prompt_helphistory_command_row(...)`
- changed runtime `helphistory` to reuse the same shared summary helper
- added focused prompt coverage for populated and empty inventories

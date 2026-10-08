# Rev640: buffer/mark root summaries stay truthful

## What changed

Plain `buffer`, `mark`, and `markjump` used to go oddly blind at their root entry points.

- Before Enter, their exact command-bar rows still showed generic command metadata even though Micromax already knew the live buffer or mark register those commands were about to target.
- After Enter with no arguments, they jumped straight to `usage:` without first showing the same current register humans were being asked to choose from.

Rev640 keeps the fix deliberately small.

- `_prompt_buffer_command_row(...)` now reuses `_buffer_inventory_preview_summary()` for plain `buffer`.
- `_prompt_mark_command_row(...)` now reuses `_mark_inventory_preview_summary()` for plain `mark` and `markjump`.
- `_buffer_runtime_root_summary(...)` and `_mark_runtime_root_summary(...)` now keep that same witness visible on the raw no-arg paths before `usage:`.

## Why it matters

This is a trust/flow cleanup.

When the user is deciding which buffer to switch to or which named mark to set or jump to, the editor should not make them mentally reconstruct the current register from memory or from a second command. The root command itself already knows enough to provide one compact witness.

That keeps the headless command surface calmer and more legible for humans, tests, and future scriptable UIs:

- one tiny substrate for the same inventory truth,
- no extra policy hidden in the TUI,
- no drift between pre-Enter and post-Enter feedback,
- and less generic `usage:`-only behavior at the exact moment a user wants orientation.

## Tests

Focused tests pin both halves of the behavior.

- prompt preview: plain `buffer`, `mark`, and `markjump` reuse the live inventory summaries before Enter,
- runtime roots: raw `buffer`, `mark`, and `markjump` print the same summary before `usage:`.

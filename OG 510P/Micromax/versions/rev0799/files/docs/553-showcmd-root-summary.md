# Rev612: keep plain `showcmd` truthful at the root

## Why

Micromax already had everything needed to answer the question behind plain `showcmd` without guessing:

- `command_detail_row(NAME)` / `ed.command-detail-row` exposed exact command doc, group, and provenance.
- `ed.cmd-rows` exposed the live command register for scripts and future UIs.
- nearby exact root inspectors like `showhook`, `showkeymode`, and `showoption` had already stopped going generic before and after Enter.

But the exact command inspector still had one small trust seam. Typing plain `showcmd` in the command bar fell back to generic command metadata before Enter, and running raw `showcmd` printed only `usage: showcmd NAME`. That hid whether the live command register was all builtins or already extended by plugins/user config.

## What changed

- added shared `_command_inventory_preview_summary()` in `Editor`
- plain `showcmd` command-bar completion now reuses that summary
- raw runtime `showcmd` now prints the same summary before `usage: showcmd NAME`
- the summary prefers one grouped/plugin command sample when available, otherwise the first stable command row
- focused tests pin both prompt and runtime root behavior

## Result

The root exact command inspector stays small and usage-shaped, but it no longer goes blind at the moment a human or future LLM is trying to orient itself. `showcmd` now says what command inventory is actually live before it asks for one exact command name.

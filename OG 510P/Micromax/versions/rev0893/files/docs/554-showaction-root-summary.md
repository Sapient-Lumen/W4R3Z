# Rev613: keep plain `showaction` truthful at the root

## Why

Micromax already had everything needed to answer the question behind plain `showaction` without guessing:

- `action_detail_row(NAME)` / `ed.action-detail-row` exposed exact action doc and best-effort provenance.
- generic action-topic completion and `commandpick` already reused that exact action metadata during discovery.
- nearby exact root inspectors like `showhook`, `showkeymode`, `showoption`, and `showcmd` had already stopped going generic before and after Enter.

But the exact action inspector still had one small trust seam. Typing plain `showaction` in the command bar fell back to generic command metadata before Enter, and running raw `showaction` printed only `usage: showaction NAME`. That hid whether the live action register was only builtins or already extended by plugins, local config, or test helpers.

## What changed

- added shared `_action_inventory_preview_summary()` in `Editor`
- plain `showaction` command-bar completion now reuses that summary
- raw runtime `showaction` now prints the same summary before `usage: showaction NAME`
- the summary prefers one non-core action sample when available, otherwise the first documented stable action row
- focused tests pin both prompt and runtime root behavior

## Result

The root exact action inspector stays small and usage-shaped, but it no longer goes blind at the moment a human or future LLM is trying to orient itself. `showaction` now says what action inventory is actually live before it asks for one exact action name.

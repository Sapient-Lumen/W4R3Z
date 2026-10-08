# Recent picker selected-slot truth

Rev517 closes one small trust seam in Micromax's recent-file picker loop.

Micromax already had the nearby honest surfaces:

- plain `recent` showed stable pre-open MRU slot numbers
- rev514 made direct `recent N` execution keep the chosen slot in its final feedback
- rev516 made `recentpick` / `recentdirpick` submit feedback keep a visible `#N` slot instead of dropping slot identity entirely

But one mismatch still lingered exactly where picker browse became action:

- picker-submit feedback looked up the MRU row again *after* the reopen succeeded
- reopening a selected file naturally bumps it to the front of the MRU list
- that meant choosing a row labeled `#3` could immediately answer back as `recentpick #1 -> ...`

## What changed

Rev517 keeps the change deliberately small.

- `submit_prompt()` now snapshots the selected recent-file slot before it delegates to `open`
- `format_recent_picker_feedback(...)` accepts that pre-submit slot and prefers it over the post-open MRU row
- successful `recentpick` / `recentdirpick` submits now keep the slot the human or future LLM actually selected, even though the reopen still moves that file to the front of the MRU list afterward
- focused tests pin both picker submit paths and explicitly prove that MRU promotion still happens underneath the preserved feedback

## Why it matters

This is tiny, but it keeps picker feedback truthful.

When a recent-file picker shows one row as `#N`, the final message should keep that same selected slot instead of silently switching to the file's new post-open MRU position. Preserving the chosen slot makes the picker loop line up with the visible row you actually acted on.

## Focused tests

- `tests/test_editor_buffer_lifecycle_recent.py`

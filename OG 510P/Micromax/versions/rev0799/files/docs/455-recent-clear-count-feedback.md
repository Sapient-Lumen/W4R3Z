# Recent clear count-aware feedback

Rev513 closes one small trust seam in Micromax's recent-file loop.

Micromax already had the nearby honest surfaces:

- plain `recent` showed the MRU inventory with tiny file/state truth
- rev512 made command-bar completion for `recent [N|clear]` explicit, including a `clear history` row with a forget-count cue
- `recent clear` already did the right state change by forgetting the MRU register and persisting that empty list

But one mismatch still lingered at the moment of execution:

- the destructive preview said how many remembered files would be forgotten
- the actual command still answered with a bare `recent cleared`
- that made the completion row more informative than the command you eventually ran

## What landed

Rev513 keeps the change deliberately small.

- `Editor.clear_recent_files()` now returns the number of forgotten MRU entries
- `recent clear` reports `recent cleared: forgot N recent file(s)`
- the empty case stays explicit too: `recent cleared: forgot 0 recent files`
- focused tests pin both the non-empty and already-empty paths

## Why this matters

This is tiny, but it keeps destructive feedback honest.

If Micromax already knows how many remembered files it is about to forget — and the command bar already previews that number — the command should report that same fact after execution. That keeps the preview, the state change, and the final message in one plainspoken dialect.

## Focused tests

- `tests/test_editor_buffer_lifecycle_recent.py`

# Recent picker slot-aware submit feedback

Rev516 closes one small trust/flow seam in Micromax's recent-file picker loop.

Micromax already had the nearby honest surfaces:

- plain `recent` showed the MRU inventory with stable slot numbers plus tiny file/state truth
- rev512 made command-bar completion for `recent [N|clear]` explicit enough to preview numbered reopen targets before Enter
- rev514 made direct `recent N` execution keep the chosen MRU slot in its final feedback
- rev515 made `recentpick` / `recentdirpick` submit feedback keep the picker route visible instead of falling back to generic `opened: ...`

But one mismatch still lingered at the exact moment picker browse became action:

- the selected target still came from recent state
- the final picker message kept the picker route but dropped the MRU slot number
- that made picker-submit feedback slightly thinner than the numbered `recent` inventory and completion surfaces around it

## What changed

Rev516 keeps the change deliberately small.

- `Editor.format_recent_picker_feedback(label, path)` now reuses the exact recent-file row before formatting the final message
- when that row still maps to one live MRU slot, successful picker submits report `recentpick #N -> path @ line:col` or `recentdirpick #N -> path @ line:col`
- the existing tiny `existing file` / `new file` plus `current buffer` / `switch buffer` truth stays attached when Micromax already knows it
- focused tests pin both picker submit paths

## Why it matters

This is tiny, but it keeps the recent-file loop coherent.

Once Micromax already knows that one picker submit came from recent slot `#N`, the final message should keep that same slot-aware truth. Keeping the slot visible makes it easier for humans and future LLMs to line the executed picker action back up with the numbered `recent` inventory and command-bar previews beside it.

## Focused tests

- `tests/test_editor_buffer_lifecycle_recent.py`

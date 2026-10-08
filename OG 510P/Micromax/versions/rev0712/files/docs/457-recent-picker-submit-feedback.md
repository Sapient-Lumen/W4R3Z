# Recent picker submit feedback

Rev515 closes one small trust/flow seam in Micromax's recent-file picker loop.

Micromax already had the important nearby pieces:

- plain `recent` showed MRU inventory plus tiny disk/action truth
- rev512 made command-bar completion for `recent [N|clear]` explicit enough to preview numbered reopen targets before Enter
- rev514 made direct `recent N` execution keep the chosen slot number and landed file/action truth instead of falling back to generic `opened: ...`
- dedicated `recentpick` / `recentdirpick` prompts already showed the same honest row metadata while you browsed

But one small mismatch still lingered at the exact moment of picker submit:

- selecting a file from `recentpick` or `recentdirpick` still delegated final feedback to generic `open`
- the picker route disappeared right after Enter even though the surrounding recent surfaces were already more specific

## What changed

- `Editor.submit_prompt()` now rewrites successful `recentpick` / `recentdirpick` file-open feedback after the underlying open succeeds
- one tiny `Editor.format_recent_picker_feedback(label, path)` helper keeps that rewrite local and reuses the existing exact recent-file truth row
- successful picker submits now report `recentpick -> path @ line:col` or `recentdirpick -> path @ line:col`
- when Micromax already knows them, the same tiny `existing file` / `new file` plus `current buffer` / `switch buffer` cues stay attached
- focused tests pin both picker submit paths

## Why it matters

This is tiny, but it keeps the whole recent-file loop coherent.

Once Micromax already knows that a file was chosen from a recent-aware picker, where that selection landed, and whether the target is an existing file or just a buffer switch, the final message should keep that recent-specific truth. Falling back to generic `opened: ...` made the picker execute like a thinner dialect than the browse rows and direct `recent N` path around it.

## Touched

- `src/micromax_editor/editor.py`
- `tests/test_editor_buffer_lifecycle_recent.py`

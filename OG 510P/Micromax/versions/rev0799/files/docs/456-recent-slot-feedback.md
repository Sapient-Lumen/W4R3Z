# Recent slot-aware reopen feedback

Rev514 closes one small trust/flow seam in Micromax's recent-file loop.

Micromax already had the nearby honest surfaces:

- plain `recent` showed the MRU inventory with tiny file/state truth
- rev512 made command-bar completion for `recent [N|clear]` explicit, including numbered rows with file/action cues
- rev513 made `recent clear` report the same forget-count its preview already promised

But one mismatch still lingered on the positive reopen path:

- choosing `recent N` still executed through generic `open` feedback
- the final message forgot which MRU slot you actually picked
- that made the executed command less specific than the inventory and completion rows around it

## What landed

Rev514 keeps the change deliberately small.

- successful `recent N` still reuses the existing open path and capability checks
- after the reopen lands, Micromax rewrites the final success message to `recent N -> path @ line:col`
- that final message also appends the same tiny `existing file` / `new file` plus current `current buffer` truth Micromax already knows after the reopen
- focused tests pin the numbered reopen path directly

## Why this matters

This is tiny, but it keeps the recent-file loop coherent.

If Micromax already knows which recent slot you chose, where it landed, and whether that target is an existing file or a scratch reopen, the final message should say that recent-specific truth. Falling back to generic `opened: ...` wording made the actual command feel thinner than the preview and inventory surfaces around it.

## Focused tests

- `tests/test_editor_buffer_lifecycle_recent.py`

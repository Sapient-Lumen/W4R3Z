# Recent-file location dedupe

Rev506 closes one small but noisy taste/trust seam in Micromax's recent-file
surfaces.

Micromax already had the right recent-file truth nearby:

- palette `Recent Files` rows kept MRU state plus tiny `existing file` /
  `new file` and `current buffer` / `switch buffer` cues
- exact `showrecent PATH` inspection reused the same recent-file register and
  exposed the same disk/action truth without reopening anything
- rev505 had already taught palette recent rows to spend their `info` slot on
  landing context instead of repeating a basename already visible in `menu`

But one tiny repetition seam still lingered inside those same rows:

- when a recent file lived directly under its visible section root, palette
  `Recent Files` rows could still say `section=/tmp/demo | /tmp/demo | ...`
- plain `showrecent PATH` could do the same thing for exact recent-file
  inspection, even though the second copy added no new location truth

## What landed

Rev506 keeps the follow-up deliberately small.

- `Editor._recent_location_parts(...)` now centralizes recent-file
  location-text assembly so recent surfaces can keep the broad `section=...`
  cue without repeating the same directory again as a second location field
- command-palette `Recent Files` rows now reuse that helper, so top-level files
  under one visible root stay honest without wasting space on `root | root`
- plain `showrecent PATH` now reuses the same helper too, so exact inspection
  keeps the same deduped location story as the adjacent palette row

## Why this matters

This is a tiny taste/trust cleanup.

Micromax spends a lot of effort making small rows tell the truth before Enter.
Once the row already says which broad section owns a recent file, repeating the
same directory again is just noise. Collapsing that duplicate keeps the row more
legible without hiding any actual location information.

## Focused tests

- `tests/test_command_palette_path_completion.py`
- `tests/test_editor_buffer_mru_and_closeall.py`
- `tests/test_editor_mx_commands_and_completion.py`

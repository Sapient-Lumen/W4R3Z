# Rev670 - badge `macro play last` as the default slot

## What changed

Micromax now keeps the default-slot story visible in the exact playback rows too.

- exact `macro play last` / `macro run last` rows now render `last (N step[s]) [default]`
- exact playback count rows for `last` now keep that same `[default]` badge
- other saved playback rows like `demo (N step[s])` stay unchanged

## Why it matters

Rev669 fixed the idle playback roots, but one token later the exact playback row still flattened `last` back into an ordinary saved macro. That was tiny, but it made the most common replay slot feel less special exactly where the user chose it.

This rev keeps the language boring and legible:

- root playback says replay defaults to `last`
- the slot menu keeps `last` first
- the exact playback row for `last` now says `[default]`

## Verification

Focused prompt tests pin both the exact slot row and the exact count row for saved `last`.

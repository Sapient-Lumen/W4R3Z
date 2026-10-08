# Rev671 - let `macro play last` say `play default slot`

## What changed

Micromax now keeps the default-slot language visible in the exact playback action text too.

- exact `macro play last` / `macro run last` rows now say `play default slot`
- exact playback count rows for `last` now say `play default slot Nx`
- other saved playback rows like `demo (N step[s])` still keep the generic `play macro` / `play Nx` wording

## Why it matters

Rev670 added the `[default]` badge, but the action text still flattened `last` back into a generic slot. That was tiny, but it made the most common replay target read less intentionally than the root and menu surfaces around it.

This rev keeps the prose aligned:

- root playback says replay defaults to `last`
- the slot row for `last` shows `[default]`
- the action text for `last` now says `play default slot`

## Verification

Focused prompt tests pin both the exact slot row and exact count row wording for saved `last`.

# Rev674 - badge saved `last` in plain macro inventory output

## What changed

Micromax now keeps the default replay slot visibly marked in the plain inventory strings too.

- `macro_list_entries()` now emits `last (N step[s]) [default]`
- `macro list` now shows `last (N step[s]) [default]`
- the saved-entry tail of idle `macro status` now shows `last (N step[s]) [default]`

## Why it matters

The broader macro/status/play surfaces already taught that replay defaults to `last`, but the plain inventory strings still flattened `last` into an ordinary saved macro. That was tiny, but it made the simplest inventory output less legible than the richer views around it.

This rev keeps the inventory dialect aligned:

- the default slot is marked in exact rows
- the default slot is marked in broad status summaries
- the default slot is now marked in plain list output too

## Verification

Focused runtime/helper tests pin both `macro list` and idle `macro status` saved-entry wording.

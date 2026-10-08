# Rev664 - keep empty `last` inspectable

## What changed

Micromax now keeps the default macro replay slot visible even before anything has
been saved there.

- `macro_detail_row("last")` now returns `['last', 'last', 'saved', 0, 1, 0]` instead of `None`
- `showmacro last` now reports `showmacro last [default]: 0 steps · default replay slot` instead of `showmacro: no such macro: last`
- exact `showmacro` completion now always offers `last`, so the command bar can preview that default-empty state before Enter too

## Why

Rev660 deliberately kept `get_macro("last")` special because `last` is the
default replay slot. Rev661 stopped advertising empty named macros as saved
inventory. Rev663 then added an exact `showmacro NAME` / `ed.macro-detail-row`
inspection lane.

That left one tiny seam: the special slot `last` was still reported as missing
whenever it was idle and empty. That answer was technically consistent with the
saved-inventory rules, but it was misleading for the one slot Micromax still
treats specially by default.

## Result

Exact inspection now distinguishes between these cases more honestly:

- named empty slot like `ghost` → missing
- default slot `last` with no saved steps yet → visible at `0 steps [default]`
- recording-owned `last` or target slot → visible as live steps
- saved slot → visible with saved step count

This is deliberately small, but it tightens both **trust** and **flow**:

- trust, because Micromax stops claiming its one default replay slot does not exist
- flow, because users, scripts, and future LLMs can inspect `last` directly before deciding whether to record, play, or overwrite it

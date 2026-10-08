# Rev668 - keep default-slot macro menus `last`-first

## What changed

Micromax now keeps `last` first across the macro slot menus that teach or use the default slot.

- exact `showmacro` slot completion still leads with `last`
- `macro play` / `macro run` now keep saved `last` first when it is playable
- fresh `macro record` / `macro rec` / `macro start` now offer explicit `last` instead of an empty slot menu
- record menus also keep `last` first when other macro names exist

## Why

Rev664 through rev667 made the default macro slot much more honest: `showmacro last` stopped pretending the slot was missing, root `showmacro` stayed centered on `default=last (N steps)`, and the exact `showmacro` slot menu started putting `last` first.

That left one narrow adjacent seam in the action menus. The minute a user moved from inspection into `macro play` or `macro record`, the slot menus could still reorder names alphabetically or hide `last` completely on a fresh editor.

## Result

The default-slot story now stays consistent across the next-step menus too.

Examples:

- fresh `macro record ` now offers `last`
- with saved `last` and `demo`, both `macro play ` and `macro record ` now offer `last` before `demo`

This is deliberately small, but it improves both **flow** and **trust**:

- flow, because the first menu choice now matches the slot most users are likely to want
- trust, because the action menus no longer contradict the docs and root summaries that already describe `last` as the default macro slot

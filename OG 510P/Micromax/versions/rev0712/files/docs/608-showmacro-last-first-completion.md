# Rev667 - make `showmacro` completion lead with `last`

## What changed

Micromax now keeps `last` at the front of the exact `showmacro` slot menu.

- `showmacro` slot completion now preserves a `last`-first order
- the rest of the menu still dedupes names and keeps fuzzy fallback behavior intact
- exact rows for the chosen candidates are unchanged; only the candidate order is calmer and more intentional

## Why

Rev664 through rev666 steadily made the exact macro inspector more honest: `showmacro last` stopped pretending the default slot was missing, root `showmacro` started mentioning `default=last (N steps)`, and idle root summaries kept that default-slot witness visible even when other macros existed.

That left one quiet flow seam: the slot menu itself still re-sorted candidates alphabetically, so `last` could show up below unrelated names right after the root inspector had just taught the user that `last` was the default exact target.

## Result

The root exact-inspector story and the next-step menu now agree.

Examples:

- with saved `last` and `demo`, `showmacro ` now offers `last` before `demo`
- typing `showmacro l` still jumps straight to `last` as before

This is deliberately small, but it improves both **flow** and **trust**:

- flow, because the default slot is now the first easy choice instead of an alphabetical afterthought
- trust, because the menu order now matches the behavior and docs Micromax already teaches elsewhere

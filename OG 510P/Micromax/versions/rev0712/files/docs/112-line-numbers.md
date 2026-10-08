# Line numbers / ruler (rev171)

Micromax now has a tiny **optional** line-number gutter in the curses TUI.

## Options

- `ruler` (bool, default `false`) — show line numbers
- `relativeruler` (bool, default `false`) — when `ruler=true`, show relative numbers away from the current line while the current line keeps its absolute 1-based number

Examples:

```forth
set ruler true
set relativeruler true
```

## Current policy

This stays intentionally small and UI-facing:

- the gutter is a **TUI concern**, not headless buffer state
- gutter width is `digits(total logical lines) + 1`, leaving one spacer column before buffer text
- wrapped continuation rows keep a **blank gutter** so softwrap does not repeat the same number on every visual row
- the current line number renders bold; non-current numbers render dim in the minimal curses TUI
- prompt lines, picker suggestions, and the statusline still use the full terminal width

## Why this shape

Micro documents a `ruler` option plus a `relativeruler` companion, which is the right ergonomic reference point for a micro-esque editor. Micromax keeps the first implementation smaller and safer by making the gutter optional and limiting it to the TUI layer for now, while still reusing the same option names so config muscle memory ports cleanly.

## Tests

- `tests/test_tui_ruler.py` covers absolute numbers, relative numbers, wrapped continuation blanks, and cursor offset behavior.

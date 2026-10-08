# Guide-column cue / `colorcolumn` (rev179)

Rev179 adds a tiny `colorcolumn` option to the minimal curses TUI.

## What it does

- `colorcolumn` (int, default `0`)
- when set to a positive column number, the TUI highlights that single visible
  guide column with the same simple reverse+dim cue used by other tiny scanability
  overlays
- the cue is visual-only: it does not change buffer contents or add persistent
  span/state to the headless editor model

## Scope / policy

This first pass is intentionally tiny and renderer-local:

- in ordinary horizontally scrolled views, the configured value is treated as a
  **document column** and compared against the fragment's starting column, so the
  cue moves on/off screen honestly with horizontal scrolling
- under `softwrap`, the configured value is treated as a **screen column** and
  repeats on each wrapped visual row
- if the guide column lands past the end of a short visible row, the renderer
  still draws a one-cell blank marker so the cue remains visible

That keeps the behavior useful without promising a richer logical-column overlay
model or tab-expanded visual-column engine yet.

## Why this shape

micro already exposes `colorcolumn` as a plain numeric option, which is a good fit
for Micromax's current headless-first editor core: a useful scanability affordance
without needing a deeper diagnostics/layout subsystem first.

Neovim's docs make the useful distinction that `colorcolumn` is fundamentally a
**screen-column** highlight concept. For Micromax that argues for a tiny policy:
be honest about horizontal scrolling in ordinary views, and let wrapped visual rows
repeat the cue instead of pretending there is already a smarter logical-column
projection across wraps.

## Files

- option: `src/micromax_editor/editor.py::_install_default_options`
- renderer helper: `src/micromax_editor/tui.py::colorcolumn_screen_x`
- tests: `tests/test_tui_colorcolumn.py`, `tests/test_portability_suite.py`

# Rev221 — shared visible viewport-row model

Rev216–rev220 moved almost the entire tiny reference screen into shared editor-side
models: layout, edit window, prompt panel, whole-screen composition, and
visible gutters.

One practical gap remained: future UIs, scripts, tests, and LLMs still had to
zip `edit_window_model(...)` and `gutter_model(...)` together by `screen_y` to
answer the boring question “what visible edit rows are on screen right now?”

Rev221 closes that gap with one tiny shared helper and host surface:

- `viewport_rows_model(lines, cols)`
- hostcall / convenience word: `ed.viewport-rows` / `viewport-rows`

## What the model reports

The model is intentionally tiny and text-first. It reports:

- viewport geometry (`x`, `y`, `width`, `height`)
- gutter widths (`left_width`, `right_width`)
- ordered visible `rows` with stable:
  - `view_y` / `screen_y`
  - buffer `line` / `start_col` / `continuation`
  - visible fragment `text`
  - `left_text` for the line-number cell
  - `right_text` for the scrollbar-thumb cell (when present)
  - `combined_text` for quick row-by-row inspection
  - `cursor_here` / `cursor_x`

That gives future UIs, scripts, tests, and LLMs one inspectable answer to
questions like:

- Which visible edit rows are on screen right now?
- Which line-number cell belongs to each visible fragment?
- Which rows currently carry the scrollbar thumb?
- Which visible row contains the cursor?

## Why this stayed small

GNU nano still describes the interface as a handful of simple screen regions,
and Micromax has been steadily moving only tiny shared truths out of the
renderer. A row-ordered viewport snapshot fits that pattern better than a richer
paint API or widget abstraction.

## TUI reuse

The minimal curses TUI now reuses the shared viewport-row model for:

- visible edit rows
- visible left line-number cells
- visible right-edge scrollbar-thumb rows

Styling still stays in `tui.py`; the shared editor core only owns the boring
text/position contract.

## Portability sibling

The same rev also adds one more nested exception case to the JSON portability
corpus: `nested-catch-throw-preserves-outer-visible-return-stack-value`.

That keeps the exception contract honest about visible `r@`: once an inner
`throw` is caught and control returns to the outer protected region, an outer
user-pushed return-stack item should still be visible and later removable via
`r>`.

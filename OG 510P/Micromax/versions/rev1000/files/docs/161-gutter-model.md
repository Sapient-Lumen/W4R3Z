# Rev220 — shared visible gutter model

Rev216–rev219 moved most of the tiny reference screen into shared editor-side
models: layout, edit window, prompt panel, bottom rows, and the composed screen.
One visible region still lived mostly in `tui.py`: the gutters.

Rev220 lifts that remaining visible gutter truth into one small shared helper and
host surface:

- `line_number_gutter_text(...)`
- `scrollbar_thumb_span(...)`
- `scrollbar_thumb_char()`
- `gutter_model(lines, cols)`
- hostcall / convenience word: `ed.gutter-model` / `gutter-model`

## What the model reports

The model is intentionally tiny and text-first. It reports:

- `left_width` / `right_width`
- `line_numbers_active` / `scrollbar_active`
- `scrollbar_x`
- `line_numbers`: visible left-gutter cells with stable `screen_y`, `text`, and
  current-line markers
- `scrollbar_rows`: visible thumb rows with stable `screen_y`, `screen_x`, and
  one-cell `text`

That gives future UIs, scripts, tests, and LLMs one inspectable answer to
questions like:

- Which visible edit rows have line-number cells right now?
- What exact text is in those cells?
- Where is the scrollbar thumb?

## Why this stayed small

GNU nano still describes the interface as a few simple screen regions instead of
a richer widget tree, and Micromax has been steadily moving only the tiny shared
truths out of the renderer. A gutter snapshot fits that pattern better than a
larger paint or widget abstraction.

## TUI reuse

The minimal curses TUI now reuses the shared gutter model for:

- visible line-number cells
- visible right-edge scrollbar-thumb rows

Styling still stays in `tui.py`; the shared editor core only owns the boring
text/position contract.

## Portability sibling

The same rev also adds one more nested exception case to the JSON portability
corpus: `nested-catch-throw-counts-only-outer-user-return-stack-items`.

That keeps the exception contract honest about visible `rdepth`: once an inner
`throw` is caught and control returns to the outer protected region, only outer
user-pushed return-stack items should count there.

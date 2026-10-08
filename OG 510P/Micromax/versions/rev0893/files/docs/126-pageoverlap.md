# Page overlap / shared paging context (rev185)

Rev185 adds a tiny shared `pageoverlap` option to the editor core.

## Option

- `pageoverlap` (int, default `0`)

Meaning:
- keep that many rows from the previous view visible when `PageUp` / `PageDown`
  moves the window
- applies in the shared editor action behavior, so headless tests, the curses TUI,
  and future frontends all inherit the same paging rule automatically
- under `softwrap=true`, the overlap is measured in **visual rows** (wrapped
  fragments), not logical document lines

The effective page jump is:
- `max(1, page_height - pageoverlap)`

So overlap can never make paging stall completely.

## Why this shape

micro's current options docs explicitly define `pageoverlap` as the number of
lines from the current view to keep in view when paging.

For Micromax, the important design choice was to keep the first pass **shared-core**
instead of renderer-local:
- `PageUp` / `PageDown` now move cursors by the effective page step
- they also shift the shared viewport origin by that same step
- softwrapped views do the same thing in visual-row space via `top_subline`

That means future UIs, scripts, and LLMs do not need to guess how paging is
supposed to compose with viewport state.

## Conservative default

micro defaults `pageoverlap` to `2`, but Micromax starts at `0` for now.

That keeps existing page-jump expectations stable while still making the shared
paging contract available to configs/tests immediately.

## Portability side note

The same rev also teaches the portability corpus one more tiny lookup-only
truth: `dict-version` stays stable across `get-current` too.

## Files/tests

- editor core: `src/micromax_editor/editor.py`
- docs: `docs/43-worklist.md`, `docs/94-softwrap.md`, `docs/50-editor-behaviors.md`
- tests: `tests/test_editor_tier0_basics.py`, `tests/test_editor_softwrap.py`, `tests/test_portability_suite.py`

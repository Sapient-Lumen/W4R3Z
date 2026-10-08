# Scrollbar thumb glyph / `scrollbarchar` (rev181)

Rev181 adds a tiny `scrollbarchar` option to the minimal curses TUI.

## What it does

- `scrollbarchar` (str, default `|`)
- controls the **one-cell glyph** used for the existing right-edge scrollbar thumb
- only affects the renderer's visible thumb text; it does **not** change thumb
  sizing, viewport math, or the headless editor model

## Scope / policy

This follow-up intentionally keeps the scrollbar contract tiny and unchanged:

- the scrollbar remains exactly **one column** wide
- empty values fall back to `|`
- longer strings use only their **first** visible character
- ordinary buffers, docs/help buffers, and `softwrap` views all reuse the same
  glyph policy because they already reuse the same scrollbar thumb sizing logic

That keeps the feature useful for readability/personal taste without promising a
richer theme API, multi-cell glyph support, or a separate scrollbar track model.

## Why this shape

Rev180 already landed the right small scrollbar model:
- reserve one right-edge column
- derive a passive thumb from the viewport the renderer already knows
- keep softwrap honest by measuring wrapped visual rows there
- leave richer styling for later renderers

The obvious next tiny improvement was therefore not a new scrollbar subsystem,
but one micro-esque customization knob: let users choose the thumb glyph while
keeping the one-column contract intact.

## Portability side note

The same rev also adds one more namespace/search-order corpus case:
`search-order-prefers-first-entry-on-conflict`.

That pins down a useful real lookup guarantee for future Rust/WASM hosts:
when multiple active wordlists define the same name, the first searched entry
wins.

## Files

- option: `src/micromax_editor/editor.py::_install_default_options`
- renderer helper: `src/micromax_editor/tui.py::scrollbar_thumb_char`
- corpus: `portability/kernel_cases.json`
- tests: `tests/test_tui_scrollbar.py`, `tests/test_portability_suite.py`

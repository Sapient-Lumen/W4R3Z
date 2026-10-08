# Tiny overflow markers (`overflowmarkers`)

Rev183 adds a deliberately small, renderer-local overflow cue to the curses TUI.

## What it does

- `overflowmarkers` (bool, default `false`)
- when enabled, horizontally clipped rows can show tiny edge cues:
  - `<` means hidden content exists to the **left** of the viewport
  - `>` means hidden content exists to the **right** of the viewport
- ordinary editable buffers and protected docs/help buffers share the same cue
- the cue is visual-only: it does not change buffer contents or add persistent
  overflow state to the headless editor model

## Scope / policy

This first pass stays intentionally tiny:

- markers only appear in **non-softwrap** views, where horizontal clipping would
  otherwise be easy to miss
- under `softwrap`, markers are intentionally suppressed because the wrapped rows
  already expose continuation implicitly and a cue on every visual row would be
  noisy
- markers are drawn directly on the visible left/right edge cells of the row
  instead of introducing a new gutter or track
- when only one cell is available, the right marker wins so the cue still hints
  that the line continues forward

## Why this shape

Micromax's recent TUI work has gone best when cues stay small and local:
`cursorline`, `hltrailingws`, `hltaberrors`, `colorcolumn`, `scrollbar`, and
`matchbrace` all landed as option-driven overlays rather than new shared editor
subsystems.

Overflow fits the same pattern. The renderer already knows when a row is clipped.
The smallest honest thing to do is expose that fact visually without inventing a
new viewport-decoration model or a richer theme system first.

## Portability side note

The same rev also teaches the portability corpus one more dictionary contract:
`dict-version` should bump on definitions, but remain stable across lookup-only
operations like successful `find`.

## Files

- option: `src/micromax_editor/editor.py::_install_default_options`
- renderer helper: `src/micromax_editor/tui.py::overflow_marker_cells`
- corpus: `portability/kernel_cases.json`
- tests: `tests/test_tui_overflowmarkers.py`, `tests/test_portability_suite.py`

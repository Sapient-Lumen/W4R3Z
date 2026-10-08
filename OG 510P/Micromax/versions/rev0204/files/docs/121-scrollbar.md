# Right-edge scrollbar cue / `scrollbar` (rev180)

Rev180 adds a tiny `scrollbar` option to the minimal curses TUI.

## What it does

- `scrollbar` (bool, default `false`)
- when enabled, the TUI reserves one right-edge screen column for a proportional
  thumb when the document is taller than the visible viewport
- the cue is visual-only: it does not change buffer contents or add persistent
  scrollbar state to the headless editor model

## Scope / policy

This first pass is intentionally tiny and renderer-local:

- in ordinary views, thumb size/position are derived from **logical rows**
- under `softwrap`, thumb size/position are derived from **visual rows** so the
  cue reflects wrapped scrolling honestly
- docs/help buffers use the same cue as ordinary editable buffers
- when the document already fits in the viewport, the reserved column stays blank
  instead of drawing a fake full-height track

That keeps the feature useful without promising a richer scrollbar widget,
click-handling model, or shared viewport-decoration contract.

## Why this shape

The recent Micromax TUI work has gone well when cues stay small and option-driven:
`ruler`, `cursorline`, `hlsearch`, `hltrailingws`, `hltaberrors`, and
`colorcolumn` all landed as ordinary display toggles rather than deeper editor
subsystems.

For a scrollbar, the smallest good move is the same:
- reserve one column
- derive a passive thumb from the viewport the renderer already knows
- keep softwrap honest by measuring wrapped **visual rows** there
- leave richer track/thumb styling or mouse interaction for later renderers

## Portability side note

The same rev also teaches the portability corpus a tiny new trick: cases may now
optionally include `host_features` so positive host-boundary probes like
`host.feature?` success and sorted `host.features` inventory stay data-only.

## Files

- option: `src/micromax_editor/editor.py::_install_default_options`
- renderer helpers: `src/micromax_editor/tui.py::{scrollbar_gutter_width,scrollbar_thumb_span}`
- portability runner: `src/micromax/portability_suite.py`
- corpus: `portability/kernel_cases.json`
- tests: `tests/test_tui_scrollbar.py`, `tests/test_portability_suite.py`

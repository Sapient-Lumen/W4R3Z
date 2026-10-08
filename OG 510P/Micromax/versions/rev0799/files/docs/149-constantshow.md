# Tiny `constantshow` infobar cue

Micromax now honors a tiny nano-esque `constantshow` option in the curses TUI.

## What it does

When the editor is **idle** (no active prompt) and the infobar row is visible:

- the left side still shows the most recent message, if any
- `constantshow=true` adds a **right-aligned** compact cursor summary:
  - `Ln <line>/<lines>, Col <col> (<percentage>%)`
- when space is tight, the right-side summary wins over the left message

Examples:

- `saved                  Ln 1/5, Col 1 (0%)`
- `                      Ln 42/120, Col 9 (35%)`

When a prompt is active, the prompt still owns that row entirely; the constant-show
cue does **not** get appended to command/find/picker input.

## Why this shape

This is intentionally small and renderer-local:

- micro's current options docs still treat `infobar` and `statusline` as simple
  bottom-bar surfaces rather than a larger widget system
- GNU nano's current manual still treats `constantshow` as a modest status-bar cue
  that keeps cursor position visible all the time
- Micromax already had the meaningful shared substrate in `status_model()`
  (`display_line`, `display_col`, `line_count`, `percentage`, `last_message`)

So the Micromax-sized move was **not** a bigger headless status subsystem. It was
one tiny TUI helper that reuses the shared model and composes with the recent
`infobar` / `statusline=false` row-reclaim work.

## Implementation notes

- option: `constantshow` (default `false`)
- helper: `constantshow_text(ed)`
- helper: `infobar_text(ed, width=...)`
- renderer wiring: `src/micromax_editor/tui.py::_render`

The current cue deliberately stays out of `status_model()` because the *layout* is
renderer-specific even though the underlying data is shared.

## Portability follow-up

This rev also cleans up one tiny cross-host truth in the JSON portability corpus:

- `return-stack-roundtrip` now actually round-trips a value through `>r ... r>`
- `return-stack-peek-and-depth` remains the separate case that covers `r@`, `rdepth`,
  and `rdrop`

That keeps the corpus easier to read by name during future Rust/WASM bring-up.

## Files touched

- `src/micromax_editor/editor.py`
- `src/micromax_editor/tui.py`
- `tests/test_tui_keymenu.py`
- `portability/kernel_cases.json`
- `tests/test_portability_suite.py`

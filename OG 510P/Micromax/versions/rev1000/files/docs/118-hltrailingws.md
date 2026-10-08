# Trailing-whitespace cue / `hltrailingws` (rev177)

Rev177 adds a tiny `hltrailingws` option to the minimal curses TUI.

## Option

- `hltrailingws` (bool, default `false`)

Meaning:
- reverse-dim visible trailing spaces/tabs at the ends of logical lines
- keep the feature renderer-local instead of storing warning spans in the headless editor model
- apply the same cue in ordinary buffers, docs/help buffers, softwrapped final fragments, and horizontally scrolled views

## Fragment policy

The first pass is intentionally explicit about what gets highlighted.

Trailing whitespace is computed from the **logical line**, then intersected with the
**current visible fragment**:
- under `softwrap`, only the final wrapped fragment that actually contains the trailing
  spaces/tabs gets the cue
- under horizontal scroll, only the visible scrolled slice gets the cue
- non-trailing interior spaces stay untouched

## Why this way

micro already exposes `hltrailingws` as a simple display toggle, which is a good fit
for Micromax's current size.

For Micromax, the smallest good move is:
- keep the option in the ordinary editor option registry
- let the current curses renderer derive one tiny cue from the visible fragment it
  already owns
- avoid pretending Micromax already has a fuller diagnostics model or a stable notion
  of "freshly typed" versus "forgotten" trailing spaces

## Portability side note

The same rev also adds `previous-drops-top-search-order-entry` to
`portability/kernel_cases.json`, making one more search-order contract explicit for
future Rust/WASM hosts.

## Pointers

- option defaults: `src/micromax_editor/editor.py`
- renderer helper: `src/micromax_editor/tui.py::trailing_whitespace_spans`
- tests: `tests/test_tui_hltrailingws.py`, `tests/test_portability_suite.py`

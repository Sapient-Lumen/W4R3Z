# Current-row cue / `cursorline` (rev176)

Rev176 adds a tiny `cursorline` option to the minimal curses TUI.

## Option

- `cursorline` (bool, default `true`)

Meaning:
- underline the **current visible buffer row** in the curses TUI
- keep the feature renderer-local instead of storing current-line highlight spans in
  the headless editor model
- apply the same cue in ordinary buffers, docs/help buffers, and the optional ruler gutter

## Softwrap policy

The first pass is intentionally explicit about wrapped lines.

When `softwrap=true`:
- only the **active wrapped screen row** under the primary cursor gets the cue
- sibling wrapped fragments of the same logical line stay unhighlighted
- this keeps the policy tiny and inspectable instead of pretending Micromax already
  has a richer logical-line highlight model

## Why this way

Micro documents `cursorline` as a simple display toggle rather than a deeper editor-state
feature. Neovim's `cursorline` / `cursorlineopt=screenline` split is a useful reminder
that wrapped views already have more than one honest policy.

For Micromax, the smallest good move is:
- keep the option in the ordinary editor option registry
- let the current curses renderer derive one tiny cue from the visible row model it
  already owns
- leave room for a future theme/span system to revisit the exact styling later

## Portability side note

The same rev also adds `definitions-follows-top-of-search-order` to
`portability/kernel_cases.json`, making one more namespace/search-order contract explicit
for future Rust/WASM hosts.

## Pointers

- option defaults: `src/micromax_editor/editor.py`
- renderer helper: `src/micromax_editor/tui.py::cursorline_row_attr`
- tests: `tests/test_tui_cursorline.py`, `tests/test_portability_suite.py`

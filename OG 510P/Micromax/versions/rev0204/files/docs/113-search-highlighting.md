# Search highlighting / `hlsearch` (rev172)

Micromax already exposed an `hlsearch` option in the editor option registry.
Rev172 makes the minimal curses TUI actually honor it.

## Behavior

- `hlsearch` (bool, default `false`) — highlight visible matches for the current search pattern
- highlighted matches use a small renderer-only cue:
  - ordinary visible matches render **reverse-video**
  - the visible match under the primary cursor also renders **bold**
- the feature follows the existing editor search state:
  - literal vs regex mode
  - `ignorecase` / case-sensitive behavior
  - incremental find updates when `incsearch` is enabled

This stays intentionally **TUI-local** for now.
The headless editor model still owns the search pattern and cursor movement,
but not a permanent “highlight spans” data structure.
That keeps future renderers free to style search matches differently.

## Scope

The first pass is deliberately tiny and renderer-oriented:

- it highlights **visible row fragments** in the current viewport
- it works in ordinary buffers and docs/help buffers
- under softwrap or horizontal scrolling, highlighting is based on the visible
  fragment text the TUI is already rendering, instead of reconstructing a
  hidden full-width layout model

That is enough to make repeated matches easier to scan without committing the
project to a larger renderer contract yet.

## Example

```text
set hlsearch true
```

Then search as usual with `Find`, `FindLiteral`, `FindRegex`, `FindNext`, and
`FindPrevious`.

## Tests

- `tests/test_tui_hlsearch.py` covers literal/regex span detection plus visible
  match rendering for current vs non-current matches.

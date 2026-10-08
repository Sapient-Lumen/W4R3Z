# Shared visible search-row model (rev223)

Micromax now publishes one tiny viewport-local `search_rows_model(lines, cols)` snapshot plus hostcall `ed.search-rows`.

## Why

- `hlsearch` was already useful in the minimal curses TUI, but the actual visible match spans still lived only in renderer code.
- Recent shared screen helpers (`screen_layout_model(...)`, `edit_window_model(...)`, `viewport_rows_model(...)`, `screen_rows_model(...)`) made the next honest question obvious: **which visible row fragments currently match the active search, and which visible match owns the cursor?**
- The answer should stay smaller than a whole-buffer style API: just the visible viewport rows, their spans, and the current match.

## Shape

- `search_rows_model(lines, cols)`
- hostcall / convenience word: `ed.search-rows` / `search-rows`
- composed sibling: `screen_model(lines, cols)["search_rows"]`

The model is text-first and viewport-local:

```text
{
  active: 1|0,
  enabled: 1|0,
  query: "...",
  literal: 1|0,
  case_sensitive: 1|0,
  y: <viewport y>,
  x: <viewport x>,
  width: <viewport width>,
  height: <viewport height>,
  row_count: <visible row count>,
  match_rows: <rows with at least one visible match>,
  rows: [
    {
      view_y: 0,
      screen_y: 0,
      line: 12,
      start_col: 0,
      text: "visible fragment",
      spans: [[a, b], ...],
      current_spans: [[a, b], ...],
      match_count: n,
      current_match_count: m,
    },
    ...
  ]
}
```

## Notes

- `active` means there is a current search query.
- `enabled` mirrors the existing `hlsearch` option. When it is off, rows are still aligned with the visible viewport, but `spans`/`current_spans` stay empty.
- Spans are always relative to the row's visible `text` fragment, not to hidden off-screen columns.
- `current_spans` is the subset of visible spans that currently contains the primary cursor.

## Scope

This intentionally does **not** generalize into a whole-buffer paint model, syntax-theme API, or persistent highlight index. It is one tiny visible-cue snapshot that future UIs/tests/scripts/LLMs can inspect directly while the reference curses TUI remains free to choose actual attributes/colors.

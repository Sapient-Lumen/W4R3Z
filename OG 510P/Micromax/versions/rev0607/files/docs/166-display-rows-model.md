# Shared display-text screen rows (rev225)

Micromax now publishes one tiny `display_rows_model(lines, cols)` snapshot plus hostcall `ed.display-rows`.

## Why

- `screen_rows_model(...)` already answered the question "what plain screen rows exist right now?", but it intentionally stopped short of the last tiny renderer overlays.
- The remaining honest visible-text gap was small but real: `showchars` replacements and horizontal `overflowmarkers` changed what the user actually saw, yet future UIs/tests/scripts/LLMs still had to recompute those overlays by hand.
- The answer should still stay smaller than a paint/theme API: just the final displayed row text plus a few tiny viewport-row facts about what changed.

## Shape

- `display_rows_model(lines, cols)`
- hostcall / convenience word: `ed.display-rows` / `display-rows`
- composed sibling: `screen_model(lines, cols)["display_rows"]`

The model mirrors `screen_rows_model(...)`, but viewport rows now carry the final display text the reference curses TUI paints:

```text
{
  active: 1|0,
  lines: <screen lines>,
  cols: <screen cols>,
  row_count: <visible row count>,
  rows: [
    {
      screen_y: 0,
      kind: "viewport"|"prompt-panel"|"interaction"|...,
      text: "final visible row text",
      raw_text: "plain pre-overlay row text",
      display_changed: 1|0,
      cursor_here: 1|0,
      cursor_x: n|-1,

      # viewport rows only
      line: 12,
      start_col: 0,
      continuation: 0|1,
      viewport_text: "raw viewport fragment",
      viewport_display_text: "final viewport fragment",
      overflow_cells: [[x, "<"|">"], ...],
      overflow_count: n,
      overflow_left: 1|0,
      overflow_right: 1|0,
    },
    ...
  ]
}
```

## Notes

- `text` is the final row text after tiny shared visible-text policy is applied.
- `raw_text` keeps the older plain row contract for callers that want to diff or explain what changed.
- For non-viewport rows (`prompt-panel`, `interaction`, `statusline`, etc.), `text` and `raw_text` are identical.
- For viewport rows, `viewport_display_text` currently layers only two tiny text-changing cues: shared `showchars` replacements and shared horizontal overflow markers.
- Styling remains out of scope. Search highlighting, cursorline, brace matching, markdown emphasis, and similar attribute-only cues still belong to renderer styling, not to this text-first model.

## Scope

This intentionally does **not** become a full paint model, syntax-theme contract, or rich cell-grid engine. It is one tiny shared visible-text snapshot so future UIs/tests/scripts/LLMs can inspect the same row text the reference curses TUI paints without scraping curses output or redoing overlay policy by hand.

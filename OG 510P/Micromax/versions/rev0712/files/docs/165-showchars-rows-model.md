# Shared visible `showchars` row model (rev224)

Micromax now publishes one tiny viewport-local `showchars_rows_model(lines, cols)` snapshot plus hostcall `ed.showchars-rows`.

## Why

- `showchars` was already useful in the minimal curses TUI, but the actual visible replacement text and spans still lived only in renderer code.
- Recent shared screen helpers (`edit_window_model(...)`, `viewport_rows_model(...)`, `screen_rows_model(...)`, `screen_model(...)`) made the next honest question obvious: **what invisible-character replacements are currently visible on screen, and where are they?**
- The answer should stay smaller than a general paint/style API: just the visible row fragments, their visible replacement text, and replacement spans.

## Shape

- `showchars_rows_model(lines, cols)`
- hostcall / convenience word: `ed.showchars-rows` / `showchars-rows`
- composed sibling: `screen_model(lines, cols)["showchars_rows"]`

The model is text-first and viewport-local:

```text
{
  active: 1|0,
  enabled: 1|0,
  spec: "tab=>,space=.,itab=|>,ispace=|",
  y: <viewport y>,
  x: <viewport x>,
  width: <viewport width>,
  height: <viewport height>,
  row_count: <visible row count>,
  changed_rows: <rows with at least one visible replacement>,
  rows: [
    {
      view_y: 0,
      screen_y: 0,
      line: 12,
      start_col: 0,
      text: "\t a\tb",
      display_text: "|:a>b",
      spans: [[a, b], ...],
      replacement_count: n,
    },
    ...
  ]
}
```

## Notes

- `active` / `enabled` are both true when the parsed `showchars` spec contains at least one supported replacement key.
- `text` is the raw visible row fragment from the shared edit-window model.
- `display_text` is the visible fragment after the tiny one-cell replacement policy is applied.
- Spans are always relative to the row's visible fragment.
- Softwrap continuation-indent prefix spaces remain plain because they are renderer-created, not file content.
- `ispace` / `itab` still override ordinary `space` / `tab` glyphs only inside the logical line's leading indent run.

## Scope

This intentionally does **not** generalize into a broader theme/span API, a multi-cell glyph layout engine, or a new buffer-text model. It is one tiny visible-cue snapshot that future UIs/tests/scripts/LLMs can inspect directly while the reference curses TUI remains free to choose actual attributes/colors.

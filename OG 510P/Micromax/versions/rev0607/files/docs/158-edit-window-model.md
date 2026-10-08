# Rev217 — shared edit-window model

Rev212–rev216 already moved the visible **bottom chrome** and its **screen
layout** into tiny shared editor-side models:

- `bottom_rows_model(width)` / `ed.bottom-rows`
- `statusline_model(width)` / `ed.statusline-model`
- `keymenu_model(width)` / `ed.keymenu-model`
- `infobar_model(width)` / `ed.infobar-model`
- `interaction_model(width)` / `ed.interaction-model`
- `screen_layout_model(lines, cols)` / `ed.screen-layout`

The remaining renderer-private truth was the **edit window itself**: which
buffer fragments are visible, where wrapped continuation rows begin, and where
the primary cursor lands on screen.

Rev217 adds one tiny shared sibling:

- `edit_window_model(lines, cols)`
- hostcall / convenience word: `ed.edit-window` / `edit-window`

## Shape

Example (abridged):

```json
{
  "lines": 8,
  "cols": 40,
  "viewport_x": 3,
  "viewport_y": 0,
  "viewport_width": 36,
  "viewport_height": 6,
  "rows": [
    {
      "view_y": 0,
      "screen_y": 0,
      "screen_x": 3,
      "line": 0,
      "start_col": 0,
      "text": "hello world",
      "continuation": 0
    }
  ],
  "row_count": 1,
  "viewport": {
    "top_line": 0,
    "top_subline": 0,
    "left_col": 0,
    "height": 6,
    "width": 36
  },
  "cursor": {
    "view_y": 0,
    "view_x": 5,
    "screen_y": 0,
    "screen_x": 8,
    "visible": 1
  },
  "softwrap": 0
}
```

## Notes

- This is a **live view snapshot**, not a purely static geometry helper.
- Unlike `screen_layout_model(...)`, it intentionally syncs viewport
  size/origin the same way the reference renderer does before painting.
- `rows[*].text` is plain visible buffer text only.
  - It does **not** include line-number gutter strings.
  - It does **not** include styling spans, search highlights, brace cues,
    showchars substitutions, or overflow-marker overlays.
- `continuation=1` means the row begins partway through a softwrapped logical
  line.

## Why this exists

This gives future UIs, tests, scripts, and LLM handoffs one more boring,
inspectable source of truth:

- what the reference renderer considers visible edit-window rows
- how those rows map back to logical buffer lines + start columns
- where the primary cursor lands on screen after layout + follow-cursor logic

That is enough for many debugging/inspection tasks without scraping curses
output or re-deriving viewport math by hand.

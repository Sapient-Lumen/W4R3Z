# Rev218 — shared visible-screen model

Rev212–rev217 already moved the visible reference screen into several tiny
shared editor-side pieces:

- `bottom_rows_model(width)` / `ed.bottom-rows`
- `statusline_model(width)` / `ed.statusline-model`
- `keymenu_model(width)` / `ed.keymenu-model`
- `infobar_model(width)` / `ed.infobar-model`
- `interaction_model(width)` / `ed.interaction-model`
- `screen_layout_model(lines, cols)` / `ed.screen-layout`
- `edit_window_model(lines, cols)` / `ed.edit-window`

That was already useful, but future UIs/scripts/LLMs still had to stitch those
pieces together by hand to answer the simplest question: **what does the whole
reference screen look like right now?**

Rev218 adds one tiny composed sibling:

- `screen_model(lines, cols)`
- hostcall / convenience word: `ed.screen-model` / `screen-model`

## Shape

Example (abridged):

```json
{
  "lines": 10,
  "cols": 30,
  "layout": {
    "viewport_width": 30,
    "viewport_height": 7,
    "prompt_y": 8,
    "status_y": 9
  },
  "edit_window": {
    "row_count": 3,
    "rows": [
      {"view_y": 0, "screen_y": 0, "line": 0, "text": "alpha"}
    ]
  },
  "bottom_rows": [
    {"kind": "keymenu", "slot": "help", "y": 7, "text": "^Q Quit  ..."},
    {"kind": "interaction", "slot": "prompt", "y": 8, "text": ":status ..."},
    {"kind": "statusline", "slot": "status", "y": 9, "text": "t.mx ..."}
  ],
  "cursor": {
    "mode": "prompt",
    "screen_y": 8,
    "screen_x": 7,
    "visible": 1
  }
}
```

## Notes

- This is intentionally a **composition helper**, not a brand-new renderer model.
- `layout` is the same shared geometry snapshot from `screen_layout_model(...)`.
- `edit_window` is the same shared live view snapshot from `edit_window_model(...)`.
- `bottom_rows[*]` merges visible row text with the already-shared `y` positions.
- `cursor` answers the final “where would the terminal cursor go?” question:
  - `mode="edit"` when the primary buffer cursor is active
  - `mode="prompt"` when an ordinary prompt is active on the prompt row

## Why this exists

This gives future UIs, tests, scripts, and LLM handoffs one boring place to inspect:

- the whole reference screen geometry
- the visible edit-window rows
- the currently visible bottom chrome, with positions
- the final active cursor placement

That is enough for many debugging and handoff tasks without scraping curses
output or calling several smaller host surfaces and recombining them manually.

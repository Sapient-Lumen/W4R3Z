# rev216 — shared reference screen-layout model

Rev212–rev215 already moved the *visible bottom rows themselves* into small shared editor-side models:

- `bottom_rows_model(width)` — ordered visible bottom chrome rows
- `statusline_model(width)` — left/right/padding/truncation for the status row
- `keymenu_model(width)` — visible shortcut rail
- `infobar_model(width)` — idle message + constantshow summary row
- `interaction_model(width)` — visible prompt/capture row

But one last piece of actual UI truth was still trapped in the curses renderer: how much of a given terminal is left for editing after gutters, picker suggestions, and bottom rows are reserved.

Rev216 lifts that into one tiny shared reference helper and hostcall:

- `screen_layout_model(lines, cols)`
- `ed.screen-layout` / `screen-layout`

## Returned shape

```python
{
  "lines": 12,
  "cols": 40,
  "viewport_x": 3,
  "viewport_y": 0,
  "viewport_width": 36,
  "viewport_height": 6,
  "suggestions_y": 6,
  "suggestions_height": 3,
  "suggestions_width": 36,
  "gutter_left": 3,
  "gutter_right": 1,
  "scrollbar_x": 39,
  "bottom_rows_count": 3,
  "chrome_top_y": 9,
  "prompt_y": 10,
  "status_y": 11,
  "keymenu_y": 9,
  "bottom_rows": [
    {"kind": "keymenu", "slot": "help", "y": 9},
    {"kind": "interaction", "slot": "prompt", "y": 10},
    {"kind": "statusline", "slot": "status", "y": 11},
  ],
}
```

The model is intentionally about **geometry**, not repeated text. If a future UI or
LLM also needs the visible row contents, it should combine this with
`bottom_rows_model(width)`.

## Why this exists

This keeps one more real piece of UI behavior inspectable for:

- future UIs that want to mimic the reference curses layout without scraping it
- tests that want to assert layout agreement without reverse-engineering viewport math
- future LLMs reading the archive who need one place to understand where the editor is actually drawing things

The minimal curses TUI now reuses this shared layout model for viewport reservation and bottom-row placement, so the archive has one more boring, inspectable source of truth instead of another block of layout arithmetic hidden in renderer code.

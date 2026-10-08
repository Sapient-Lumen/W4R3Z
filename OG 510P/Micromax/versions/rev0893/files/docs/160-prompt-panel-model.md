# Rev219 — shared visible prompt-panel model

Rev140–rev148 already moved picker position/window/rendering policy into tiny
shared editor-side helpers:

- `prompt_current_position()` / `ed.prompt-current-position`
- `prompt_window_model(max_lines)` / `ed.prompt-window`
- `prompt_display_model(max_lines, width)` / `ed.prompt-display`

Rev216–rev218 then moved the rest of the reference screen into inspectable
shared models (`screen_layout_model`, `edit_window_model`, `screen_model`).

That still left one visible region awkwardly split across several helpers:
**the actual picker suggestion panel on screen**. Future UIs/scripts/LLMs could
inspect the rendered suggestion rows, but they still had to separately infer the
reserved panel height and screen `y` positions.

Rev219 adds one tiny sibling:

- `prompt_panel_model(lines, cols)`
- hostcall / convenience word: `ed.prompt-panel` / `prompt-panel`

## Shape

Example (abridged):

```json
{
  "active": 1,
  "kind": "palette",
  "lines": 10,
  "cols": 30,
  "y": 7,
  "x": 0,
  "width": 30,
  "screen_width": 30,
  "height": 2,
  "row_count": 2,
  "entries": [
    {
      "type": "header",
      "text": "-- Commands (4) --",
      "screen_y": 7,
      "screen_x": 0
    },
    {
      "type": "row",
      "text": "> showstatus — status line",
      "selected": 1,
      "screen_y": 8,
      "screen_x": 0
    }
  ]
}
```

## Notes

- This is intentionally a **composition helper**, not a new picker subsystem.
- `height` / `y` / `width` come from the same shared layout reservation policy
  already used by `screen_layout_model(...)`.
- `entries[*]` reuse the same rendered row metadata already produced by
  `prompt_display_model(...)`, but now carry stable `screen_y` / `screen_x`
  placement too.
- Command/find prompts still report an inactive panel because they do not paint
  the multi-row suggestion region used by picker-style prompts.

## Why this exists

This makes `screen_model(...)` more honest about the whole visible reference
screen and gives future UIs, tests, scripts, and LLM handoffs one boring place
to inspect:

- whether a picker suggestion panel is visible at all
- where it starts on screen
- how tall it is
- which rendered rows are visible there right now

That keeps the reference curses UI inspectable without scraping curses output or
recombining layout + prompt-display helpers by hand.

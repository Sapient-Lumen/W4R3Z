# Keymenu / infobar row models (rev214)

Rev212 made the **ordered bottom-row stack** inspectable, and rev213 made the
**statusline layout** inspectable, but two visible row surfaces were still more
opaque than they needed to be:

- the keymenu help rail
- the idle infobar/message row

Rev214 adds tiny sibling row snapshots so future UIs, scripts, tests, and LLMs
can inspect those rows without scraping dimmed curses output.

## New shared helpers

- `Editor.keymenu_model(width)`
- `Editor.infobar_model(width)`

## New host surface

- `ed.keymenu-model` — `( width -- m )`
- `ed.infobar-model` — `( width -- m )`
- convenience words: `keymenu-model`, `infobar-model`

## `keymenu_model(width)`

```text
{
  "active": 0|1,
  "width": n,
  "context": "normal|command|find|palette|qreplace|openurl|...",
  "entries": [{"key": "^Q", "label": "Quit", "text": "^Q Quit"}, ...],
  "text": "single visible keymenu row",
  "truncated": 0|1
}
```

Notes:
- `entries` are the real reusable contract.
- `text` is still the exact row the reference TUI draws.
- `context` tells future UIs/scripts why the shortcut set changed.

## `infobar_model(width)`

```text
{
  "active": 0|1,
  "width": n,
  "message_raw": "saved ok",
  "summary_raw": "Ln 10/120, Col 4 (8%)",
  "message": "saved ok",
  "summary": "Ln 10/120, Col 4 (8%)",
  "padding": "      ",
  "padding_width": n,
  "constantshow": 0|1,
  "truncated_message": 0|1,
  "truncated_summary": 0|1,
  "text": "saved ok      Ln 10/120, Col 4 (8%)"
}
```

Notes:
- the model is **idle-only**: active prompts/capture modes still own the prompt
  row through `interaction_*` and `bottom_rows_model(width)`
- the right summary still wins when space is tight
- `text` remains the exact shared reference row

## Why this matters

This keeps the archive friendlier to future humans and future LLMs:

- tests can assert visible bottom-row pieces without brittle text archaeology
- future UIs can reuse structured shortcut/message segments directly
- the curses renderer stays thin and mostly stylistic
- `bottom_rows_model(width)` can now reuse sibling row helpers instead of
  re-deriving each row independently

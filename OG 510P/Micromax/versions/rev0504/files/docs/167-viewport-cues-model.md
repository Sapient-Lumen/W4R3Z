# Rev226 — shared visible viewport-cue model

Rev226 lifts one more tiny piece of honest screen truth out of `tui.py` and into
shared editor-side models:

- `Editor.viewport_cues_model(lines, cols)`
- hostcall / convenience word `ed.viewport-cues` / `viewport-cues`
- composed `screen_model(lines, cols)["viewport_cues"]`

The model is deliberately **viewport-local** and **span-first**. It reports the
small non-text overlays the reference curses TUI paints on visible edit-window
rows without turning Micromax into a fuller theme or paint-engine project.

## What it exposes

For each visible edit-window row, the model reports:

- `cursorline` — whether this row owns the tiny current-row cue
- `search_spans` / `current_search_spans` — visible search-match spans reused
  from the existing shared `search_rows_model(...)`
- `showchar_spans` — visible `showchars` replacement spans reused from the
  existing shared `showchars_rows_model(...)`
- `trailing_spans` — visible trailing-whitespace cue spans
- `tab_error_spans` — visible `hltaberrors` cue spans
- `colorcolumn_spans` — in-text guide-column spans
- `colorcolumn_x` / `colorcolumn_blank` — the guide-column cell when it lands
  past the end of a short visible fragment and the TUI paints a highlighted
  blank instead
- `brace_spans` — visible matching-brace cue spans for the primary cursor

Top-level metadata also records which cue families are enabled, the current
`colorcolumn`, and the usual viewport geometry (`x`, `y`, `width`, `height`).

## Why this exists

Rev223, rev224, and rev225 already exposed:

- visible search-match spans
- visible `showchars` replacement spans/text
- the final plain row text painted after `showchars` and overflow markers

That left one awkward gap for future UIs, tests, scripts, and LLM handoffs:
**the non-text overlay math still lived inside `_render`**.

`viewport_cues_model(...)` closes that gap without overreaching. It stays:

- smaller than a theme/style API
- smaller than a whole-buffer highlight model
- smaller than a syntax/render tree

It is just one inspectable snapshot of the visible edit-window cue spans the
reference TUI already paints.

## Example shape

```python
{
  "active": 1,
  "enabled": 1,
  "cursorline_enabled": 1,
  "hlsearch_enabled": 1,
  "showchars_enabled": 0,
  "hltrailingws_enabled": 1,
  "hltaberrors_enabled": 0,
  "colorcolumn": 80,
  "matchbrace_enabled": 1,
  "rows": [
    {
      "view_y": 0,
      "screen_y": 0,
      "line": 12,
      "start_col": 0,
      "text": "alpha(beta)  ",
      "cursorline": 1,
      "search_spans": [[0, 5]],
      "current_search_spans": [[0, 5]],
      "showchar_spans": [],
      "trailing_spans": [[11, 13]],
      "tab_error_spans": [],
      "colorcolumn_x": 79,
      "colorcolumn_blank": 1,
      "colorcolumn_spans": [],
      "brace_spans": [[5, 6], [10, 11]],
      "cue_count": 5,
    },
  ],
}
```

## Renderer relationship

The minimal curses TUI now reuses this shared cue model instead of recomputing
those row-local spans ad hoc.

Actual terminal attributes still remain renderer policy:

- search spans still choose `A_REVERSE`
- current matches still add `A_BOLD`
- trailing/tab/colorcolumn cues still choose reverse+dim
- brace cues still honor `matchbracestyle`
- `showchars` cues still dim the replacement cells

So the shared model owns **where** the visible cues are, while the TUI still
owns **how** to style them.

# rev215 — shared interaction-row model

Rev211 already made the active prompt/capture interaction visible in `status_model()` through the `interaction_*` fields, but future UIs/scripts/LLMs still had to re-ellipsize that raw `interaction_line` text themselves if they wanted the *visible* bottom-row prompt/capture surface.

Rev215 closes that gap with one tiny shared helper and hostcall:

- `Editor.interaction_model(width)`
- `ed.interaction-model` — `( width -- m )`
- `interaction-model` — convenience word

## Shape

```json
{
  "active": 0|1,
  "width": 80,
  "kind": ""|"command"|"find"|"palette"|"topic"|"binding"|"qreplace"|"openurl",
  "prefix": ""|":"|"/"|"?",
  "summary": ""|":open README.md"|"?replace [1/2]",
  "detail": ""|"Commands: showstatus — show portable statusline summary"|"one -> X"|"https://...",
  "position": ""|"1/3"|"2/9 • Commands 2/6",
  "raw_line": ""|":status  [1/4 • Commands 1/4]  | Commands: showstatus — show portable statusline summary",
  "text": ""|":status  [1/4 • Commands 1/4]  | Commands: showstatus — show portable statusline summary",
  "truncated": 0|1
}
```

## Policy

- width-aware sibling of `interaction_status_model()`
- keeps the existing shared prompt/capture metadata intact
- adds the final visible row text that the minimal curses TUI would actually paint for that width
- uses the same tiny right-ellipsis policy as the other bottom-row helpers
- stays inactive (`active=0`) when there is no ordinary prompt and no capture keymode

## Why this is small but useful

This keeps the bottom-row helper family honest and complete:

- `interaction_model(width)` — visible prompt/capture row
- `keymenu_model(width)` — visible help row
- `infobar_model(width)` — visible idle message row
- `statusline_model(width)` — visible status row
- `bottom_rows_model(width)` — visible ordered bottom chrome stack

Future UIs, scripts, tests, and LLM handoffs can now inspect every visible bottom row without scraping curses output or reimplementing clipping logic.

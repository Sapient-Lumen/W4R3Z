# Shared bottom-row chrome model (rev212)

Micromax's recent TUI/editor polish passes have been converging on the same lesson:

- the bottom of the screen is still just a few tiny terminal regions
- future UIs/scripts/LLMs should be able to inspect those regions without scraping curses output
- styling can stay renderer-local even when row **semantics** become shared

Rev212 turns that lesson into one small contract.

## Surface

New shared editor helper:

- `Editor.bottom_rows_model(width: int) -> list[map]`

New host surface:

- `ed.bottom-rows` — `( width -- rows )`
- convenience word: `bottom-rows`

## Row shape

`bottom_rows_model(width)` returns the currently visible bottom chrome as a list
of row maps ordered **top-to-bottom** exactly as the minimal curses TUI paints
those rows.

Each row map is intentionally tiny:

```text
{
  "kind": "keymenu"|"interaction"|"infobar"|"statusline",
  "slot": "help"|"prompt"|"status",
  "text": "single rendered line already clipped to WIDTH"
}
```

Examples:

```text
[
  {"kind": "keymenu", "slot": "help", "text": "^Q Quit  ^S Save  ^F Find ..."},
  {"kind": "infobar", "slot": "prompt", "text": "saved ok                Ln 10/120, Col 4 (8%)"},
  {"kind": "statusline", "slot": "status", "text": "notes.txt ... normal 10:4"}
]
```

```text
[
  {"kind": "keymenu", "slot": "help", "text": "Y/Enter Replace  N Skip  A All ..."},
  {"kind": "interaction", "slot": "prompt", "text": "?replace [1/2]  | one -> X"},
  {"kind": "statusline", "slot": "status", "text": "*scratch* ... qreplace 1:1"}
]
```

## Policy

- `keymenu` appears only when the option is enabled.
- `interaction` appears whenever an ordinary prompt or capture keymode owns the
  bottom prompt row.
- `infobar` appears only when there is **no** active interaction and `infobar`
  is enabled.
- `statusline` appears only when `statusline=true`.
- the row order is the real contract; styling stays renderer-local.

## Why this helps

Before rev212, the editor already exposed several nearby shared pieces:

- prompt current-item position
- prompt visible-window model
- prompt rendered display rows
- capture status
- current prompt/capture interaction line

But the final visible bottom-row stack still had to be reconstructed from:

- options like `keymenu`, `infobar`, `statusline`, `constantshow`
- current prompt/capture state
- renderer-local text helpers

That was fine for one curses TUI, but not ideal for:

- future terminal backends
- status/debug commands
- Micromax scripts
- future LLM handoffs trying to understand what the UI is *actually* showing

The new row model keeps the contract inspectable and boring.

## Implementation note

The curses TUI now renders from `bottom_rows_model(width)` instead of
independently rebuilding keymenu / interaction-or-infobar / statusline rows.
That keeps one source of truth for visible bottom chrome while still letting the
renderer decide attributes such as dimming the keymenu rail.

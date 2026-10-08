# Tiny `infobar` TUI pass

Micromax now honors a tiny micro-esque `infobar` option in the curses TUI.

## Behavior

When `infobar` is enabled (the default):
- the idle bottom info line stays reserved for messages
- prompts still use that same row

When `infobar` is disabled:
- the idle message row is not reserved
- the buffer gets one more visible text row
- active prompts still temporarily claim a row so command/find/picker input stays usable

## Why this shape

micro's current options docs still describe `infobar` as the line where messages are
printed, while GNU nano's manual still distinguishes a bottom status/prompt area from
its separate help lines. That makes Micromax's lowest-risk follow-up pretty clear:
keep prompts usable, but do not waste a row on idle chrome when the user has asked for
that line to disappear.

This keeps the behavior entirely in the renderer and viewport reservation logic instead
of inventing new headless editor state.

## Tests

- `tests/test_tui_keymenu.py`

## Code

- option registration: `src/micromax_editor/editor.py`
- rendering/layout: `src/micromax_editor/tui.py`

# Tiny `keymenu` TUI rail

Micromax now honors a tiny micro/nano-esque `keymenu` option in the curses TUI.

The feature stays intentionally **renderer-local**:
- no new shared editor state
- no widget/layout subsystem
- just one extra bottom-row rail with compact shortcut hints

## Behavior

When `keymenu` is enabled:
- ordinary editing shows a compact nano-style shortcut summary
- command prompts show run/cancel/history hints
- find prompts show next/cancel/history hints
- picker-style prompts show choose/cancel/move/page/section hints

## Why this shape

micro's current options docs still frame `keymenu` as a lightweight discoverability
option, not a deeper layout system. GNU nano's manual also still treats the bottom
help lines as simple always-visible shortcut rails.

That makes a tiny renderer-local line the smallest honest Micromax move: it reuses
already-shared prompt/keybinding state without promoting new chrome into the
headless editor model.

## Tests

- `tests/test_tui_keymenu.py`

## Code

- option registration: `src/micromax_editor/editor.py`
- rendering: `src/micromax_editor/tui.py`

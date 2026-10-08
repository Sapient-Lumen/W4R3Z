# TUI key decoding (rev85)

Micromax-editor's core keymap is **headless**: it expects keys as strings like
`Ctrl-e`, `Alt-n`, `Shift-UpArrow`, etc.

The minimal curses UI (`micromax-editor --tui`) must translate terminal events
into those strings.

This doc exists so future humans/LLMs can debug key issues quickly.

## The translation pipeline

- `micromax_editor.tui.decode_key_event(first, second=None)` is the single
  testable entry point.
- `_key_to_name(ch)` maps **single events** (curses `KEY_*` ints and single
  characters) into key names.

### Ctrl-Space

Many terminals encode `Ctrl-Space` as NUL (`\x00`). We map this to the key name
`Ctrl-Space` so it can be bound like any other key.

Default binding (core plugin): `Ctrl-Space` opens the command palette.

## Alt/Meta chords (ESC prefix)

Many terminals encode `Alt-x` as:

- `ESC` (`\x1b`)
- followed by `x`

In curses this often arrives as *two* input events. The TUI performs a
one-event lookahead:

- if `ESC` is followed immediately by another event, we interpret it as an
  **Alt/Meta chord**.
- otherwise it is treated as plain `Esc`.

Rules:

- `ESC` + `g`  -> `Alt-g`
- `ESC` + `P`  -> `Alt-Shift-p` (uppercase letters become explicit shift)
- `ESC` + `KEY_UP` -> `Alt-UpArrow` (when curses decodes the escape sequence)

This is intentionally a tiny MVP: it covers Alt+letters/punctuation and any
Alt+special keys that curses decodes into `KEY_*` ints.

## Debugging

- `:rawkeys on` in the TUI prints raw events instead of dispatching them.
  - Press plain `Esc` to exit raw mode quickly.

## Tests

- `tests/test_tui_key_decoding.py` covers `Ctrl-Space` and a few representative
  Alt chord cases.


## Bracketed paste (rev104)

The curses TUI enables bracketed paste mode (`CSI ? 2004 h`) so terminals wrap
pastes in `ESC[200~ ... ESC[201~`. The TUI recognizes that sequence and inserts
the pasted payload as a single chunk. The mode is disabled on exit (`CSI ? 2004 l`)
so we don't leave the terminal in a bad state.

If your terminal does *not* support bracketed paste, temporarily enable the
`paste` option to aggregate paste key-bursts into one insert.

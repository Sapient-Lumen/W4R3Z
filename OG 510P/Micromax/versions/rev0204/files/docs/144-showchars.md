# `showchars`

Micromax's minimal curses TUI now honors a tiny micro-esque `showchars` option so spaces and tabs can be displayed with visible replacement glyphs without mutating buffer text.

Option:

- `showchars` (str, default `""`)

Current format:

- comma-separated `key=value` pairs
- supported keys: `space`, `tab`, `ispace`, `itab`

Example:

```
set showchars tab=>,space=.,itab=|>,ispace=|
```

Current rule:

- `space` and `tab` apply to ordinary spaces/tabs
- `ispace` and `itab` override those glyphs in the leading indent run before the first visible character on the logical line
- the displayed glyphs are view-only and are never inserted into the file
- this first pass keeps every replacement one cell wide, so even `tab` / `itab` currently use only their first configured character
- softwrap continuation-indent prefix spaces stay plain because they are renderer-created, not file content
- the same renderer-side rule applies in ordinary buffers and help/docs buffers

This stays intentionally TUI-local for now. The shared editor core still owns the real buffer text, search state, cursor positions, and wrap model.

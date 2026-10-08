# Cursorstate snapshots (save/restore cursor+selection)

Many editor commands need to do *helper navigation* without permanently moving the
user's cursor(s). Classic patterns include Emacs' `save-excursion` and Vim
mappings that save/restore cursor position or window view.

Micromax's reference editor exposes a **portable cursor/selection snapshot**
format and a convenience hostcall to run code "save-excursion" style.

## Wire format

`ed.cursorstate` returns a single `state` value:

```
[primary [[id line col aL aC] ...]]
```

- `primary` is the primary cursor index.
- Each entry is a cursor:
  - `id` is a monotonic cursor id (used for "remove latest" semantics).
  - `line col` is the cursor position (0-based, clamped).
  - `aL aC` is the selection anchor (directed selection). If there is no
    selection anchor, the values are `-1 -1`.

This uses only ints and lists, so it is straightforward to port to Rust/WASM.

## Hostcalls

- `ed.cursorstate` `( -- state )`
- `ed.set-cursorstate` `( state -- )`
- `ed.with-cursorstate` `( q -- ok )`

`ed.with-cursorstate` saves the current state, runs `q`, and then restores the
state in a `finally`-style block.

## Example: helper search without moving the cursor

```forth
: find-preview ( "q" -- ok )
  [ "ed.find" hostcall drop ] "ed.with-cursorstate" hostcall
;
```

This will execute `ed.find` (which moves the cursor to the match) but then
restore the cursor position afterwards.

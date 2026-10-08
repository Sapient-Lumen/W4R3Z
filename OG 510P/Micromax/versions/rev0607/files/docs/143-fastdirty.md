# Fast dirty tracking (`fastdirty`) (rev202)

Micromax now treats `fastdirty` as a real ordinary editor option instead of
implicitly using one fixed dirty-buffer policy everywhere.

## Why

Before rev202, the editor effectively behaved like `fastdirty=true` all the
time: once a buffer had been edited, `dirty` stayed set until a save, even if
undo or later edits returned the text to the last clean state.

That was simple, but it made the modified flag a little too coarse once
Micromax had already grown shared `autosave`, `fileformat`, `encoding`, and
statusline behavior.

## Current rule

- `fastdirty` is now an ordinary bool option (default `false`)
- with `fastdirty=false`, the buffer compares its current text against the last
  clean baseline and clears `dirty` again when the content truly matches
- with `fastdirty=true`, the buffer uses the cheaper micro-esque rule: after the
  first edit, it stays dirty until the next successful save/open baseline reset
- the clean baseline is refreshed on ordinary buffer creation, file open, and
  successful save
- command-bar option changes, Micromax option words, and `ed.opt-set` /
  `ed.opt-set-local` hostcalls all resync existing buffers immediately

## Why this shape

Current upstream micro docs still describe `fastdirty` as the switch between a
cheap modified flag and a more accurate content-based check, rather than as a
TUI-only convenience. Micromax already had the smallest honest substrate for the
same idea:

- a tiny line-based buffer
- deterministic save/open baselines
- shared statusline / quit / autosave behavior that already depends on `dirty`

So the right move was to make the dirty policy explicit and shared, not to bolt
more special cases onto status rendering or quit warnings.

## Non-goals (for now)

Rev202 does **not** try to implement:

- micro's large-file auto-enable heuristic for `fastdirty`
- chunked/incremental hashing for huge buffers
- background dirty-state workers

## Pointers

- editor buffer model: `src/micromax_editor/buffer.py`
- editor core / option install: `src/micromax_editor/editor.py`
- command-bar + hostcall sync: `src/micromax_editor/command_dispatcher.py`, `src/micromax_editor/micromax_bridge.py`
- focused tests: `tests/test_editor_fastdirty.py`

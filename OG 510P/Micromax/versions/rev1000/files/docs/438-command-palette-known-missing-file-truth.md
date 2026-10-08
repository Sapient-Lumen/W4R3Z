# Command palette known missing-file truth (rev496)

## Problem

Rev495 taught `commandpick` to keep partial parsecursor path queries visible when a
matching target was already known through editor state instead of through the
filesystem. That closed the bigger disappearance bug, but one smaller trust seam
remained beside it: visible `menu=file` completion rows could still look like
ordinary file hits even when the backing path no longer existed on disk.

That showed up in two nearby loops:

- deleted recent files that still matched a partial parsecursor query
- unsaved open buffers surfaced as known path candidates

In both cases Micromax already knew enough to keep the row visible, but the row
text still under-described what Enter would do.

## Change

Keep the fix tiny and local to `_command_palette_open_path_row(...)`:

- for visible `menu=file` rows, do one capability-gated stat of the parsed target
- when the target is missing, append `new file`
- when the row is parsecursor-shaped and no live open buffer already gives an
  exact `goto line:col` cue, append `empty buffer @ 1:0` instead of the softer
  `cursor line:col` request cue

Already-open missing paths still keep the stronger live-buffer answer:

- `new file | current buffer | goto 1:0`

Deleted recent paths that are no longer open now say the simpler truth:

- `recent #1 | /path/to/old.md | new file | empty buffer @ 1:0`

## Why this shape

This keeps the editor honest without widening authority or adding a larger path
state model:

- the row only says more when `cap.fs-list` already allows that filesystem truth
- live buffers still outrank guesses from parsecursor text
- existing-file rows stay unchanged, so the surface area is small

The goal is simple: once Micromax decides a remembered path is worth showing as a
visible candidate, it should also tell the truth when that remembered path has
become a new-file open rather than an existing-file open.

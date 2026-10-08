# Editor marks (named navigation points)

Marks are tiny, **headless-first** navigation points inspired by Vim marks and Emacs bookmarks.

They exist to keep navigation workflows testable *before* we commit to any UI:
a mark is just a `(buffer_name, line, col)` triple.

## User-facing commands (command bar)

- `mark NAME` — set a named mark at the primary cursor
- `markjump NAME` — jump to a named mark (also pushes the jumplist)
- `marks` — list marks as a short message
- `markpick [QUERY]` — open a searchable mark picker prompt (now grouped by owning buffer in the minimal TUI)

In addition, basic multi-buffer navigation exists (very early / minimal):

- `buffers` — list open buffer names
- `buffer NAME` — switch active buffer
- `bufferpick [QUERY]` — open a searchable buffer picker prompt

## Scripting surface (hostcalls)

These are intentionally small primitives:

- `ed.buffers` ( -- names )
- `ed.active-buffer` ( -- "name" )
- `ed.set-active-buffer` ( "name" -- ok )

- `ed.marks` ( -- [[name buffer line col] ...] )
- `ed.mark-set` ( "name" -- ok )
- `ed.mark-jump` ( "name" -- ok )
- `ed.mark-section-rows` ( query -- sections ) — grouped mark picker rows as `[[buffer [[name kind menu info] ...]] ...]`

## Design notes

- Marks are *not* undo: they represent “places” rather than edits.
- `jump` pushes the jumplist so you can use the same back/forward navigation
  after scripted jumps.
- Marks are stored in the `Editor` (not per-buffer) so plugins can implement
  global navigation features later (buffers/panes/trees).

## Future extensions (not implemented yet)

- file-backed marks / bookmarks (persist across sessions)
- mark “rings” (push/pop stack of locations)
- per-buffer local marks vs global marks
- persistent (file-backed) marks / bookmarks across sessions
- mark "rings" (push/pop stack of locations)
- per-buffer local marks vs global marks

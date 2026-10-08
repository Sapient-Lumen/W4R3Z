# Editor marks (named navigation points)

Marks are tiny, **headless-first** navigation points inspired by Vim marks and Emacs bookmarks.

They exist to keep navigation workflows testable *before* we commit to any UI:
a mark is just a `(buffer_name, line, col)` triple.

## User-facing commands (command bar)

- `mark NAME` — set a named mark at the primary cursor (now reports the anchored target)
- `markjump NAME` — jump to a named mark (also pushes the jumplist, reports the landed target on success, and now fails plainly when the mark is missing)
- `marks` — list marks as a short count-aware message (now marks active-buffer ownership and the current-cursor anchor explicitly too)
- `markpick [QUERY]` — open a searchable mark picker prompt (now grouped by owning buffer in the minimal TUI)

In addition, basic multi-buffer navigation exists (very early / minimal):

- `buffers` — list open buffers as a short count-aware inventory
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

Rev333 made successful mark jumps explicit, rev337 made direct `mark NAME` placement explicit, and rev346 made plain `marks` inventory legible too: active-buffer marks now carry the same `*` owner cue used elsewhere and a mark that matches the current primary cursor gets a tiny `[here]` cue. Rev365 adds one more tiny follow-up: both plain `marks` and the nearby `buffers` inventory now start with count-aware prefixes. Rev379 closes one more tiny trust seam in that same loop: missing `markjump NAME` targets now fail plainly as `markjump: no such mark: NAME`, so dropping, listing, and revisiting navigation state stays easy to verify from the command bar alone even when the answer is zero or a named jump target is gone.

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

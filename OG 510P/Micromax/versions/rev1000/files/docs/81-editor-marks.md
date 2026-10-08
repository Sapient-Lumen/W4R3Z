# Editor marks (named navigation points)

Marks are tiny, **headless-first** navigation points inspired by Vim marks and Emacs bookmarks.

They exist to keep navigation workflows testable *before* we commit to any UI:
a mark is just a `(buffer_name, line, col)` triple.

## User-facing commands (command bar)

- `mark NAME` — set a named mark at the primary cursor (now reports the anchored target, and completion for existing names reuses exact mark metadata)
- `markjump NAME` — jump to a named mark (also pushes the jumplist, reports the landed target on success, fails plainly when the mark is missing, and now reuses exact mark metadata while choosing a target)
- `marks` — list marks as a short count-aware message (now marks active-buffer ownership and the current-cursor anchor explicitly too)
- `showmark NAME` — inspect one named mark without jumping through it
- `showmarkgroups [QUERY]` — inspect broad owning-buffer mark buckets without reopening the picker
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
- `ed.mark-inventory-rows` ( -- rows ) — tiny inspectable rows as `[name buffer position preview active here]`
- `ed.mark-detail-row` ( "name" -- row|0 ) — exact mark row as `[name buffer position preview active here]`
- `ed.mark-set` ( "name" -- ok )
- `ed.mark-jump` ( "name" -- ok )
- `ed.mark-section-rows` ( query -- sections ) — grouped mark picker rows as `[[buffer [[name kind menu info] ...]] ...]`
- `ed.mark-section-summary-rows` ( query -- rows ) — tiny broad owning-buffer summaries as `[[label count sample_name sample_detail] ...]`

## Design notes

Rev333 made successful mark jumps explicit, rev337 made direct `mark NAME` placement explicit, and rev346 made plain `marks` inventory legible too: active-buffer marks now carry the same `*` owner cue used elsewhere and a mark that matches the current primary cursor gets a tiny `[here]` cue. Rev365 adds one more tiny follow-up: both plain `marks` and the nearby `buffers` inventory now start with count-aware prefixes. Rev379 closes one more tiny trust seam in that same loop: missing `markjump NAME` targets now fail plainly as `markjump: no such mark: NAME`, so dropping, listing, and revisiting navigation state stays easy to verify from the command bar alone even when the answer is zero or a named jump target is gone. Rev418 closes the matching script seam: `mark_inventory_rows()` / `ed.mark-inventory-rows` now expose the same preview-aware active/here inventory rows that humans already see through `marks`, so future UIs/LLMs no longer need to reconstruct that richer surface from the thinner raw `ed.marks` tuples. Rev452 closes the exact sibling of that same seam: `mark_detail_row(NAME)` / `ed.mark-detail-row` and plain `showmark NAME` now expose one named mark without mutating state through `markjump NAME`, so broad mark inventory and grouped browse state no longer leave exact mark inspection trapped inside formatter-only text or jump side effects. Rev453 closes the broad-summary sibling too: `mark_section_summary_rows(QUERY)` / `ed.mark-section-summary-rows` and plain `showmarkgroups [QUERY]` now expose the same owning-buffer buckets `markpick` already browses, so future UIs/LLMs can answer what broad mark groups exist right now without reopening grouped picker state. Rev462 closes one more small completion seam in that same exact-detail loop: `mark NAME` / `markjump NAME` command-bar completion now reuses `mark_detail_row(NAME)` too, so choosing one known mark keeps owning-buffer plus active/here/preview state visible instead of degrading back to the older generic `buffer:line:col` row.

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

# Rev531 — expose tiny jumplist navigation state through `status_model()`

## Why

Micromax's jumplist loop is now fairly coherent for humans at command time:

- `jumps` shows visible `#N` entries
- `showjump INDEX|#N` inspects one exact row without mutating history
- `showjumpgroups [QUERY]` summarizes grouped `Current` / `Back` / `Forward` buckets
- `jumppick [QUERY|N|#N]` now keeps the same visible-slot dialect through preview, miss, and success paths
- `jumpback` / `jumpforward` now keep the chosen visible slot and lane truth on success

But one small headless-first seam still remained for future UIs, scripts, tests, and LLMs: the editor still had no tiny structured jumplist-navigation snapshot analogous to the existing docs-history `help_*` state. Callers could infer the current jump row by reopening `jumps` or parsing the last transient message, but not by asking one stable status question.

That matters because actionability is the real question most non-human callers ask first:

- is there a current jumplist entry?
- would `jumpback` or `jumpforward` do anything right now?
- which visible `#N` slot is current?
- where would the immediate back/forward move land?

## What changed

Rev531 keeps the follow-up deliberately small:

- new `Editor.jump_navigation_model()` returns a tiny structured jumplist snapshot
- `status_model()` now includes:
  - `jump_navigation_available` / `jump_entry_count`
  - `jump_current_*` fields for the visible current row
  - `jump_back_*` / `jump_forward_*` fields for the immediate actionable neighbors
  - `jump_navigation_scope` / `jump_navigation_persisted`
  - `jump_navigation_summary` / `jump_navigation_actions` / `jump_navigation_action_summary`
- `showstatus` / `ed.status-summary` now surface the same cues as:
  - `jump_nav='...'`
  - `jump_actions='jumpback, jumpforward'`

The row shape intentionally stays tiny and boring. It reuses the same visible-slot dialect already established elsewhere, so callers see things like:

- current: `#2 [current] a @ 2:1`
- back: `#1 [back 1] a @ 1:0`
- forward: `#3 [forward 1] a @ 5:0`

## Result

Micromax no longer requires message scraping for the simplest jumplist-navigation question. A future UI or script can ask `status_model()` once and know both:

- the current visible jumplist head
- the exact next replay actions currently available

That keeps the editor more inspectable and more replayable without inventing a larger navigation API.

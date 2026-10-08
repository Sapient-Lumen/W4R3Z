# Editor jumplist (navigation history)

A **jumplist** is navigation history: a small list of cursor/selection states that
lets you jump backward/forward through "places you've been".

This is **not undo**:
- Undo is about **edits**.
- Jumps are about **locations**.

Micromax-editor keeps a **per-buffer** jumplist, capturing the full cursor set:
- cursor positions (multi-cursor)
- selection anchors (directed)
- cursor ids (for "remove latest cursor" semantics)
- primary cursor index

## Semantics

- `PushJump` appends the current cursor/selection state.
- If you've jumped backward and then push a new jump, the "forward" tail is
  discarded (browser/Vim-style).
- Consecutive identical entries are deduplicated.
- The list is bounded (currently 100 entries).

## Actions

- `PushJump` — save current cursor/selection state to the jumplist.
- `JumpBack` — restore the previous jumplist entry.
- `JumpForward` — restore the next jumplist entry.
- `jumpback` / `jumpforward` — tiny command-bar mirrors for the same traversal.
- `jumps` — show the current jumplist register as a small count-aware inventory line.

## Hostcalls

- `ed.push-jump` ( -- ok )
- `ed.jump-back` ( -- ok )
- `ed.jump-forward` ( -- ok )
- `ed.jump-info` ( -- [index size] )
- `ed.jump-history-rows` ( -- rows ) — ordered jumplist register rows as `[lane depth index buffer position preview]`
- `ed.jump-detail-row` ( n -- row|0 ) — exact jumplist row as `[query index lane depth buffer position preview]` behind plain `showjump INDEX`
- `ed.clear-jumps` ( -- )
- `ed.jump-section-rows` ( query -- sections ) — grouped rows for future pickers/UIs (`Current` / `Back` / `Forward`)

## Default bindings (core plugin)

We currently bind:
- `Alt-j` → `PushJump`
- `Alt-LeftArrow` → `JumpBack`
- `Alt-RightArrow` → `JumpForward`

(We avoid `Ctrl-i` because many terminals treat it as `Tab`.)


## Register (rev417)

The same jumplist trail is now inspectable without opening the picker:

- Command: `jumps`
  - prints a count-aware summary of the current buffer's jumplist register
  - rows appear in register order: `current`, then `back`, then `forward`
- Hostcall: `ed.jump-history-rows`
  - returns ordered rows as `[lane depth index buffer position preview]`

This stays intentionally small. The goal is not a second navigation browser; it is a tiny, honest register surface for humans, scripts, and future UIs.


## Picker (rev64)

A jumplist is most useful when you can *see* it.

- Command: `jumppick [QUERY]`
  - opens a searchable prompt over the current buffer's jumplist
  - selecting an entry restores that cursor/selection snapshot

Notes:
- Entries are now grouped by relation to the active jump: `Current`, then `Back`, then `Forward`.
- The insert key is a **1-based jumplist index**, but fuzzy search matches the
  line preview and position metadata.
- The same grouping is available headlessly through `ed.jump-section-rows`, so future UIs/LLMs do not need to reverse-engineer picker sections from row text.

## Auto-push for jump commands (rev22)

Some commands are "jump-worthy" (they move the primary cursor far enough that users often want to go back).
When the `jumplist.auto` option is enabled (default), the command-bar commands:

- `goto`
- `jump`

will record **both** the "from" and "to" locations so that `JumpBack` can immediately return.

Rev333 is a tiny UX follow-up: successful `goto` / `jump` / `helpjump` command-path navigation now also reports the real landed target (`name @ line:col`), so the jumplist can stay correct *and* the user does not have to infer where the move ended. Rev334 closes the picker-shaped gap by making `jumppick` report that same landed target too.

## Feedback (rev341)

Rev341 makes actual jumplist traversal speak the same explicit-orientation dialect as recent `open`, `buffer`, `help`, `mark`, and committed `find` work. Successful back/forward traversal now reports the landed target:

- `jumpback: name @ line:col`
- `jumpforward: name @ line:col`

No-op traversal is explicit too:

- `jumpback: no earlier jump`
- `jumpforward: no later jump`

That applies to both the `JumpBack` / `JumpForward` actions and the tiny `jumpback` / `jumpforward` command-bar commands. The aim is small but important: when users ask to go back, the editor should confirm where “back” actually is.

## Exact inspection

Rev455 closes the small exact sibling of the jumplist loop too. If a human, script, or future UI already knows the 1-based entry index from `jumps` or `jumppick`, `showjump INDEX` and `jump_detail_row(INDEX)` / `ed.jump-detail-row` now answer the next question without mutating history:

- `[query index lane depth buffer position preview]`
- example: `showjump 1 [back 1] a @ 1:0 — one`

That keeps jumplist history coherent at three scales: flat register, grouped browse state, and one exact side-effect-free row.

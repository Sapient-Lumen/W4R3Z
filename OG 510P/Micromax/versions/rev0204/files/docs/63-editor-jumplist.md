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

## Hostcalls

- `ed.push-jump` ( -- ok )
- `ed.jump-back` ( -- ok )
- `ed.jump-forward` ( -- ok )
- `ed.jump-info` ( -- [index size] )
- `ed.clear-jumps` ( -- )
- `ed.jump-section-rows` ( query -- sections ) — grouped rows for future pickers/UIs (`Current` / `Back` / `Forward`)

## Default bindings (core plugin)

We currently bind:
- `Alt-j` → `PushJump`
- `Alt-LeftArrow` → `JumpBack`
- `Alt-RightArrow` → `JumpForward`

(We avoid `Ctrl-i` because many terminals treat it as `Tab`.)



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

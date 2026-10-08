# Multiple cursors (micro-inspired)

Multiple cursors are one of micro's headline features ("Sublime-style multiple
cursors" on the homepage) and a major UX differentiator in terminal editors.

Primary sources:

- micro homepage: https://micro-editor.github.io/
- micro default keys (macros + multiple cursors table):
  https://raw.githubusercontent.com/micro-editor/micro/master/runtime/help/defaultkeys.md
- micro keybindings (full action list includes multi-cursor actions):
  https://raw.githubusercontent.com/micro-editor/micro/master/runtime/help/keybindings.md

## What micro supports (at a glance)

From `defaultkeys.md` (raw), micro binds:

- `Alt-n` — create a new cursor from selection (or select current word)
- `Alt-Shift-Up` / `Alt-Shift-Down` — spawn cursor above / below
- `Alt-p` — remove latest multi-cursor
- `Alt-c` — remove all multi-cursors
- `Alt-x` — skip multi-cursor selection
- `Alt-m` — spawn a cursor at the beginning of every line in the selection

## What micromax-editor implements (v16)

Implemented actions (names match micro's action list where practical):

- `SpawnMultiCursorUp`
- `SpawnMultiCursorDown`
- `SpawnMultiCursorSelect` (Alt-n style: select word if needed, then add next match)
- `SkipMultiCursor` (Alt-x style: advance the primary selection to the next match)
- `RemoveMultiCursor`
- `RemoveAllMultiCursors`
- `SpawnMultiCursor` (Alt-m style: cursor at start of every selected line)


### Invariants (v16)
- Cursor list is kept in **document order**.
- The **primary cursor** is an explicit index into that list (it can move independently).
- `RemoveMultiCursor` removes the newest cursor by id (micro-style “remove latest”) while preserving document order.
- A small **selection recovery stack** exists (`ed.push-selections`/`ed.pop-selections`) to recover from accidental merges/clears.

Selection endpoints are stored as **directed** anchor+cursor pairs (Kakoune/Helix-ish). For convenience,
we provide actions like `FlipSelections` and `EnsureSelectionsForward` to control direction.
### Matching semantics

Our match selection is intentionally literal and simple right now:

- If there is no selection on the primary cursor, we select the "word" under/near
  the cursor (`[A-Za-z0-9_]+`).
- We search for the next occurrence of that exact selection (respecting the
  `ignorecase` option), and add a cursor with the same selection.

This is a good stepping stone toward more nuanced micro/VSCode behavior (e.g.
whole-word mode, regex mode, and match cycling), without building a full search
engine first.

### Utility actions

We add a few small, script-friendly actions:

- `CyclePrimaryNext` / `CyclePrimaryPrev` — cycle the primary cursor among the
  active cursors (Kakoune/Helix style).
- `CollapseToPrimary` — drop all cursors except the primary.

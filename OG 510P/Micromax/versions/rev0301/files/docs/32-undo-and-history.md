# Undo, redo, and grouping

This repo currently implements a **linear** undo/redo stack (like many simple editors).

## Definitions

- An **edit** is one undo step.
- **Undo** reverts the latest edit; **redo** re-applies it.
- Buffer-visible state includes:
  - buffer text
  - cursors, selections, cursor ids, and primary cursor index

## Grouping scripted edits

Micromax scripts often want to perform several small hostcalls but expose them as a *single* user-visible undo step.

The reference editor provides:

- `ed.with-undo` ( "desc" q -- ok )

Semantics:

1. Snapshot active buffer state (before).
2. Run `q` while suppressing internal undo recording.
3. Snapshot active buffer state (after).
4. If `after != before`, record a single undo edit with description `desc`.
5. If `q` raises, restore the `before` snapshot and record **no** undo edit.

This keeps plugin actions predictable and prevents partially-applied scripted edits.

## Cursor/selection recovery stack (not undo)

Multi-cursor workflows make it easy to accidentally clear/merge selections.
We keep a tiny per-buffer stack that is *not* part of undo history:

- `ed.push-selections`
- `ed.pop-selections`
- `ed.clear-saved-selections`

Think of it like a "selection register" rather than an undo step.

## Future directions (non-binding)

- Undo tree / branching history (powerful but more complex).
- Fine-grained undo coalescing policies (e.g. insert sessions).
- Multi-buffer transactional groups (would require a more structured edit model).

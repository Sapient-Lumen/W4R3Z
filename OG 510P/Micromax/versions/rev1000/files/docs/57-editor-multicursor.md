# Multiple cursors and repeated occurrence selection

Multiple cursors are useful only when visible selections, edit geometry, and undo
agree. Rev0968 pins the complete Micromax loop rather than treating cursor count
as the feature.

Primary sources:

- VS Code multi-cursor basics:
  https://code.visualstudio.com/docs/editing/codebasics
- Sublime Text keyboard multiple-selection behavior:
  https://www.sublimetext.com/docs/multiple_selection_with_the_keyboard.html
- Micro's current action implementation:
  https://github.com/micro-editor/micro/blob/master/internal/action/actions.go
- LSP original-document text-edit model:
  https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/

## Actions

- `SpawnMultiCursorUp` / `SpawnMultiCursorDown` — add a cursor on the adjacent logical line.
- `SpawnMultiCursorSelect` — select the primary word when needed, then add the next unoccupied matching occurrence.
- `SkipMultiCursor` — move the newest matching selection to the next unoccupied occurrence.
- `RemoveMultiCursor` — remove the newest non-primary cursor by creation ID.
- `RemoveAllMultiCursors` — retain only the primary cursor.
- `SpawnMultiCursor` — replace one line selection with a cursor at each selected line start.
- `CyclePrimaryNext` / `CyclePrimaryPrev` — change which document-ordered cursor is primary.
- `CollapseToPrimary` — drop every non-primary cursor.

## State invariants

- Cursor/anchor/id vectors are normalized together and kept in document order.
- The primary cursor is an explicit index and does not have to be newest.
- Monotonic cursor IDs retain creation order after document sorting.
- Repeated occurrence continuation is derived from the highest matching cursor
  ID in the active buffer. There is no editor-global last-match coordinate.
- Selection endpoints are directed anchor+cursor pairs; normalized ranges are
  used only for text geometry.
- Exact duplicate cursor/range results may merge under the editor's standing
  duplicate-cursor invariant.

## Matching semantics

When the primary has no non-empty selection, `SpawnMultiCursorSelect` selects the
word under/near the primary cursor (`[A-Za-z0-9_]+`). The active selection is the
literal needle. Matching is forward, line-local, non-wrapping, and respects the
existing `ignorecase` option.

The newest selected occurrence is the next search origin. Already-selected exact
ranges are skipped. Repeating select-next adds a selection; skip relocates only
the newest matching selection and preserves earlier choices. A multiline needle
is refused. Exhaustion returns false unless that invocation created the initial
primary selection.

Regex, whole-word search beyond the initial word selection, wrap, backward skip,
and cross-buffer occurrence sets are not implemented.

## Simultaneous edit semantics

Typing, newline, tab, paste, backspace, delete, cut, indentation, query-replace,
and edit hostcalls interpret all cursor ranges in one immutable pre-edit buffer.
Exact duplicate edits coalesce. Other overlap or same-start ambiguity fails
before mutation. Owner cursors land at their replacement ends; every other cursor
and retained anchor is mapped with right affinity.

One multi-location edit mutates buffer text once. The one-cursor path uses a
direct line-vector splice so ordinary typing does not rebuild the whole document.
The public screen contract and reference TUI consume the same primary/secondary
selection cues before the edit.

## Undo and macros

One ordinary action records one undo snapshot. One successful macro playback
invocation records one aggregate undo/redo transaction even when repeated or
spanning buffers. Navigation-only playback does not invent history. Commands,
extension actions, and macros containing Undo/Redo retain exact-history execution
before successful aggregation.

This transaction covers captured editor state only. External filesystem, process,
network, native, and other extension effects are not rolled back.

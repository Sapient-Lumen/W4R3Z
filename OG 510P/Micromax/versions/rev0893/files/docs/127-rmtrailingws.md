# Save-time trailing-whitespace cleanup (`rmtrailingws`) (rev186)

Rev186 adds a tiny shared `rmtrailingws` option to the editor core.

## Option

- `rmtrailingws` (bool, default `false`)

Meaning:
- when enabled, manual `save` trims trailing spaces and tabs from every buffer line before writing to disk
- the cleanup lives in the shared editor save path, so headless tests, the curses TUI, command dispatch, and `ed.save` hostcalls all inherit the same behavior automatically
- the first pass is intentionally narrow: it only strips end-of-line spaces/tabs and only during save

## Why this shape

Micromax already had the visual sibling via `hltrailingws`, but that only made forgotten junk easier to *see*.

The useful next step was to make save semantics slightly smarter without inventing a whole formatter or cleanup command set:
- trim trailing spaces/tabs
- keep the in-memory buffer synchronized with what hit disk
- clamp cursors/anchors honestly after the text shrinks
- record an undoable snapshot when cleanup changed anything

That keeps the feature shared-core and future-frontend-friendly instead of burying it in curses-only rendering code.

## Undo / buffer honesty

The cleanup happens **before** writing the file, and it updates the active buffer too.

That means:
- the saved file and the live buffer stay in sync
- undo can bring the stripped whitespace back if the user really wanted it
- future UIs/scripts do not need to guess whether save silently changed bytes on disk

## Deliberate non-goals (for now)

This rev does **not** add:
- a general-purpose “strip trailing whitespace now” command
- typing-time suppression of temporary trailing spaces
- more opinionated formatting / whitespace normalization

Those can still come later if the project needs them.

## Portability side note

The same rev also teaches the portability corpus one more search-order truth: inside a single wordlist, name lookup prefers the **most recent** definition.

## Files/tests

- editor core: `src/micromax_editor/editor.py`
- docs: `docs/43-worklist.md`, `docs/50-editor-behaviors.md`
- tests: `tests/test_editor_fs_open_save.py`, `tests/test_portability_suite.py`

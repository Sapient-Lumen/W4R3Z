# Save-time final newline (`eofnewline`) (rev187)

Rev187 adds a tiny shared `eofnewline` option to the editor core.

## Option

- `eofnewline` (bool, default `false`)

Meaning:
- when enabled, manual `save` ensures a **non-empty** buffer ends with one final `\n`
- the rule lives in the shared editor save path, so headless tests, the curses TUI, command dispatch, and `ed.save` hostcalls all inherit the same behavior automatically
- the first pass is intentionally narrow: it only appends one missing terminal newline during save, and it leaves truly empty buffers empty

## Why this shape

Micromax already had enough buffer structure to preserve a terminal newline when one
was present on disk: the line model keeps a trailing empty line for newline-terminated
text.

That made the next useful step pleasantly small:
- reuse the same shared save path that rev186 already used for `rmtrailingws`
- normalize the live buffer *before* writing so the buffer stays honest about what hit disk
- record one undoable snapshot when save changed bytes
- keep the default conservative instead of silently changing every save in existing repos

## Interaction with `rmtrailingws`

Both save-time cleanups now compose through the same normalization step.

That means a save can:
- trim trailing spaces/tabs first
- then append one final newline if the result is still non-empty and not newline-terminated
- record a single undoable save-normalization edit instead of two stacked hidden edits

Example:

- before: `"alpha   "`
- after save with both options on: `"alpha\n"`

## Deliberate non-goals (for now)

This rev does **not** add:
- forced newlines for empty files
- line-ending conversion beyond the existing UTF-8/LF policy
- autosave-specific exceptions or a separate “fix EOF newline now” command

Those can still come later if the project needs them.

## Portability side note

The same rev also teaches the portability corpus one more search-order truth:
`definitions` sets the compilation wordlist from the current top of the search order,
but later `set-order` calls do **not** silently retarget that compilation wordlist.

## Files/tests

- editor core: `src/micromax_editor/editor.py`
- docs: `docs/43-worklist.md`, `docs/50-editor-behaviors.md`
- tests: `tests/test_editor_fs_open_save.py`, `tests/test_portability_suite.py`

# Save cursor positions (`savecursor`) (rev189)

Rev189 adds a tiny shared `savecursor` option to the editor core.

## What it does

- `savecursor` (bool, default `false`)
- when enabled, Micromax remembers the **primary cursor** position for each file path
- reopening that file later restores the saved line/column (clamped honestly if the file changed)
- persistence is best-effort and still gated by `cap.persist`

Related option:

- `savecursor.file` (str, default `~/.config/micromax/cursor.json`)

The stored data is intentionally tiny JSON keyed by normalized file path.

## Why this shape

micro's current options docs still frame `savecursor` as a small ordinary editor
setting rather than a heavyweight session manager. That fits Micromax well too.

The useful first pass was therefore deliberately modest:

- reuse the existing persistence safety boundary (`cap.persist`)
- keep the data model tiny and inspectable
- remember only the primary cursor, not full multi-cursor/selection/session state
- restore during ordinary `open_file(...)` without inventing background daemons or autosave logic

That keeps the behavior easy to test headlessly and easy for future hosts/LLMs
to understand from one small JSON file.

## When positions are remembered

Micromax now remembers a file's primary cursor position on a few natural shared-core edges:

- when switching away from a buffer
- when closing a buffer
- when saving a buffer
- when the headless REPL or curses TUI exits normally

That covers the common “leave a file, come back later” workflow without adding a
richer session subsystem yet.

## Clamp / honesty rules

Restoration is intentionally conservative:

- missing persistence file → no effect
- non-file buffers / scratch buffers → no effect
- saved line beyond EOF → clamp to the last valid buffer line in the current line model
- saved column beyond the current line length → clamp to the current line end
- restoring the primary cursor clears any stale primary selection anchor instead of inventing a partial selection restore

## Deliberate non-goals (for now)

This rev does **not** add:

- undo persistence (`saveundo`)
- whole-session workspace restore
- multi-cursor / selection persistence
- per-project cursor stores
- periodic autosave of cursor state while you type

Those can still come later if the project genuinely needs them.

## Where to look

- editor core: `src/micromax_editor/editor.py`
- startup wiring: `src/micromax_editor/__main__.py`, `src/micromax_editor/tui.py`
- config/capability docs: `docs/87-editor-config.md`, `docs/32-capabilities.md`
- tests: `tests/test_editor_persistence_cap_persist.py`

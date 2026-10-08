# Rev457 — replace commands keep their own identity through failure and undo

## What changed

Micromax already had the right basic ordinary replace surfaces:

- rev329 made `replace` / `replaceall` report explicit success counts and `...: not found`
- `qreplace` already kept its own `qreplace:` prefix through the confirm-each loop
- rev342 made undo/redo speak in a typed `verb: desc -> target` dialect

But one small trust-first drift still remained in the ordinary bulk-edit loop:
`replaceall` still collapsed back to generic `replace` on a few adjacent paths.
That meant:

- protected docs/help buffers could fail as `replace: read-only buffer` even when the user ran `replaceall`
- invalid-regex failures dropped the command family entirely as `invalid regex: ...`
- undo/redo after a successful `replaceall` replay said only `replace`

Rev457 keeps the fix deliberately small.

## What landed

- `replaceall` now reports `replaceall: read-only buffer` on protected buffers
- invalid-regex failures now keep the invoked command prefix as `replace: ...` or `replaceall: ...`
- undo snapshots now record `replace` vs `replaceall` truthfully, so recovery says `undo: replaceall -> ...` / `redo: replaceall -> ...`

## Why this matters

This is a tiny follow-up, but it sits exactly where bulk-edit trust lives.

Replace commands already mutate real text, can touch many matches, and are the
same paths users reach for when they are trying to work quickly. If those paths
blur together on failure or recovery, the editor makes users infer which edit
actually ran. Keeping the command family visible is a small but meaningful trust
win:

- failures stay attributable to the verb the user actually typed
- undo/redo stop flattening bulk replace into a smaller different command
- future UIs/scripts/LLMs can rely on the default human-facing messages staying typed and boring

The goal is simple: bulk-edit commands should keep telling the truth about which
edit path actually ran, even when they fail or when you immediately undo them.

## Focused tests

- `tests/test_editor_core.py`
- `tests/test_editor_help_docs_buffers.py`

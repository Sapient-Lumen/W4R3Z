# Rev694 - macro guide sync

Date: 2026-03-28

## Why

The live macro surface had moved well past the older wording still sitting in the main macro guide. In particular:

- plain `macro` now previews live next-action truth during idle / recording / playback
- plain `showmacro` now reuses that same live root summary
- default-slot rows now wear `[default]`
- exact empty `macro play last` / `run last` paths now speak `default slot empty` instead of a missing-name dialect

## What changed

Updated `docs/58-editor-macros.md` so it now teaches:

- `macro record|rec|start`, `macro play|run`, `macro list|ls`, `macro status|st`, and the plain `macro` root with their current action-shaped summaries
- `showmacro NAME` plus plain `showmacro` with the current live root-summary behavior
- the newer default-slot playback language (`[default]`, `default slot empty`, `default slot is empty`)

## Result

Future humans and LLMs can use the main macro guide as a trustworthy overview again instead of having to cross-check it against the narrower rev docs to reconstruct the current macro dialect.

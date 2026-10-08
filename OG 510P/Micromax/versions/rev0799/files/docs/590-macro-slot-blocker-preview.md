# Rev649: exact macro slot rows keep live blockers visible too

## What changed

- exact `macro play NAME` / `macro run NAME` rows still show the slot identity in
  `row[2]`, but now reuse the parent play/run blocker witness when playback is
  already active
- exact `macro record NAME` / `macro rec NAME` / `macro start NAME` rows now
  reuse the parent record blocker witness when recording is already active or
  playback is in flight
- focused prompt-completion tests pin those blocked slot rows across canonical
  and alias spellings

## Why it matters

Micromax had already made the broader macro command surface truthful: root
subcommand rows previewed live blockers before Enter, and blocked runtime paths
already spoke up after Enter. But the exact slot rows were still one token out
of date. Once a slot name was typed, completion could quietly regress to
`play macro`, `overwrite on save`, or `record new macro` even when the live
macro state was already saying `wait for playback` or `stop or cancel first`.

That made the most specific visible row slightly less trustworthy than the
broader command row above it. Reusing the shared blocker witness keeps exact
slot rows aligned with the same live state Micromax already exposes elsewhere.

## Files

- `src/micromax_editor/editor.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `README.md`
- `TODO.md`
- `docs/01-llm-start-here.md`
- `docs/02-repo-map.md`
- `docs/43-worklist.md`
- `docs/55-editor-command-bar.md`
- `docs/64-editor-prompt-completion.md`
- `docs/66-editor-micromax-commands.md`

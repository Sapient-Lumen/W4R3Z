# Rev557: undo/redo command rows preview live recovery truth

## Why

Micromax already treated edit recovery carefully after Enter: key-driven `Undo` /
`Redo` and the matching command-bar `undo` / `redo` mirrors already reported the
traversed edit description, and empty-stack retries already failed honestly as
`nothing to undo` / `nothing to redo`.

But the command bar still lagged behind the newer trust-first previews for
saves, jumps, recent navigation, close-family commands, and quit. Right before
an edit-recovery command ran, plain `undo` and `redo` still fell back to generic
command metadata even though the editor already knew whether one recovery step
existed at all.

That left one tiny but frequent trust seam harder than it needed to be: humans
and future LLMs had to press Enter or inspect hidden stack state just to learn
whether recovery was available.

## What changed

- added shared `_prompt_undo_redo_command_preview(...)` and
  `_prompt_undo_redo_command_row(...)` helpers in
  `src/micromax_editor/editor.py`
- exact command completion for plain `undo` and `redo` now replaces generic
  provenance info with live recovery-stack truth
- previews stay deliberately small:
  - `undo` shows the next traversable edit description plus the current touched
    target when one step exists
  - `redo` does the same for the redo stack
  - empty stacks show `nothing to undo` / `nothing to redo`
- focused tests pin both command-row previews in
  `tests/test_editor_prompt_completion_hostcalls.py`

## Result

Micromax now keeps one more high-frequency recovery loop honest before Enter: if
it already knows whether `undo` or `redo` can do anything right now, the
command bar says so directly instead of hiding behind generic command metadata.

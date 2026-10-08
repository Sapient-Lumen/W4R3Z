# `showjump` command-bar preview (rev535)

## Why

Micromax already knew the current exact jump through `showjump INDEX|#N`, the live `jumps` register, the grouped `showjumpgroups` buckets, and the structured `jump_navigation_model()` snapshot. But plain `showjump` in the command bar still looked like a generic command row right before the user had to choose an explicit slot.

That was a small trust/flow seam: the command existed precisely to inspect one exact visible jumplist entry, yet the command bar hid whether any current visible jump existed at all until the caller supplied one more token or reopened a neighboring jumplist surface.

## What changed

- new `Editor._prompt_showjump_command_row(...)` reuses `jump_navigation_model()`
- exact command completion for plain `showjump` now keeps the ordinary command doc while replacing the generic info hint with:
  - `current #N [lane depth] buffer @ line:col · expects INDEX|#N` when a visible current row exists
  - `no jumps · expects INDEX|#N` when the current buffer has no jumplist entries

## Examples

- `showjump` with three entries and current slot `#2` can preview as:
  - `current #2 [current] a @ 2:1 · expects INDEX|#N`
- `showjump` with an empty register previews as:
  - `no jumps · expects INDEX|#N`

## Tests

- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showjump_command_previews_current_slot`
- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showjump_command_previews_empty_inventory`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`

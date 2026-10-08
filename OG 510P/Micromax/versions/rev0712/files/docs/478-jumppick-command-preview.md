# `jumppick` command-bar preview (rev536)

## Why

Micromax already knew the live jumplist inventory through `jumppick N|#N`, `jumps`, `showjump`, `showjumpgroups`, and the structured `jump_navigation_model()` snapshot. But plain `jumppick` in the command bar still looked like a generic command row with a blank info hint right before Enter.

That was a small trust/flow seam: the command existed precisely to browse or jump through the current visible jumplist, yet the command bar hid whether there were any visible slots at all until after execution.

## What changed

- new `Editor._prompt_jumppick_command_row(...)` reuses `jump_navigation_model()`
- exact command completion for plain `jumppick` now keeps the ordinary command doc while replacing the blank hint with:
  - `0 jumps` when the current buffer has no jumplist entries
  - `N jumps · current #N [lane depth] buffer @ line:col` when the register is populated

## Examples

- `jumppick` with three entries and current slot `#2` can preview as:
  - `3 jumps · current #2 [current] a @ 2:1`
- `jumppick` with an empty register previews as:
  - `0 jumps`

## Tests

- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_jumppick_command_previews_current_inventory`
- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_jumppick_command_previews_empty_inventory`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`

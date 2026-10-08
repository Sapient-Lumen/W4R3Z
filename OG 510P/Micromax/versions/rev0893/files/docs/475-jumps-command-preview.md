# `jumps` command-bar preview (rev533)

## Why

Micromax already knew the live jumplist register through `jumps`, `status_model()`, and the newer `jumpback` / `jumpforward` command-row previews. But plain `jumps` in the command bar still looked like a generic no-arg command right before Enter.

That was a small trust/flow seam: the command existed precisely to inspect the current visible jumplist register, yet the command bar hid whether there were any visible jump slots at all until after execution.

## What changed

- new `Editor._prompt_jumps_command_row(...)` reuses `jump_navigation_model()`
- exact command completion for plain `jumps` now keeps the ordinary command doc while replacing the generic info hint with:
  - `0 jumps` when the current buffer has no jumplist entries
  - `N jumps · #current ...` when the register is populated

## Examples

- `jumps` with three entries can preview as:
  - `3 jumps · #2 [current] a @ 2:1 <- #1 [back 1] a @ 1:0 (+1) -> #3 [forward 1] a @ 5:0 (+1)`
- `jumps` with an empty register previews as:
  - `0 jumps`

## Tests

- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_jumps_command_previews_current_inventory`
- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_jumps_command_previews_empty_inventory`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`

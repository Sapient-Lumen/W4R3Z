# Rev646 - macro alias completion parity

## What changed

The shorter macro aliases Micromax already accepted at runtime now behave like
first-class command-bar paths too:

- `macro run` previews the same saved-inventory truth as `macro play`
- `macro ls` previews the same saved inventory as `macro list`
- `macro st` previews the same live runtime snapshot as `macro status`
- `macro end` / `macro abort` preview the same recording guards as `macro stop` / `macro cancel`
- `macro run NAME` now reuses the same saved-slot rows as `macro play NAME`
- the root `macro` doc and usage line now include supported `status`

## Why it matters

This is mostly a trust/flow cleanup.

Micromax already knew these aliases after Enter, but before this loop the command
bar treated several of them as second-class: some never appeared in suggestions,
typed exact alias rows fell back to generic `macro action`, and `macro run NAME`
lost the saved-slot previews its canonical sibling already had. That mismatch made
short forms feel unofficial even though the dispatcher supported them.

## Implementation notes

- `_prompt_macro_command_row(...)` now normalizes alias subcommands onto their
  canonical preview behavior while keeping alias-specific menu text visible
- `_prompt_macro_slot_row(...)` and slot completion treat `run` like `play`
- macro subcommand completion now offers the remaining supported aliases
- `command_dispatcher.c_macro(...)` and the registered root command doc now name
  `status` so the umbrella entry point stops hiding one supported verb

## Validation

- `pytest -q tests/test_editor_prompt_completion_hostcalls.py -k macro tests/test_editor_macros_named.py`

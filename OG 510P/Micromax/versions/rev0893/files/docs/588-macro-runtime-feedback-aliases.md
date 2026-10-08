# Rev647 - macro runtime feedback alias truth

## What changed

Blocked macro runtime paths now keep the same tiny truth Micromax already
showed before Enter:

- idle `macro stop` / `end` now report `macro SUB: idle · not recording`
- idle `macro cancel` / `abort` now report the same `not recording` witness
- blocked `macro record` / `rec` / `start` attempts now echo the live
  recording guard instead of failing silently
- `macro run` now keeps alias-specific `count must be ...` and `no such macro`
  wording instead of leaking canonical `macro play` text

## Why it matters

This is a small trust cleanup.

Micromax's command bar had already become more honest about macro state than the
runtime itself: exact alias rows could tell you `idle · not recording` or
`recording · demo (1 step) · stop or cancel first`, but after Enter some of
those same paths still failed silently or answered with canonical-only wording.
That mismatch made the surface feel less reliable right at the moment the user
committed to the command.

## Implementation notes

- `_macro_subcommand_runtime_summary(...)` reuses `_prompt_macro_command_row(...)`
  so blocked runtime paths and command-bar previews share one tiny witness
- `command_dispatcher.c_macro(...)` now emits explicit state-aware feedback for
  blocked `record` / `stop` / `cancel` aliases before calling the underlying
  editor methods
- `macro run` now validates count and slot existence with alias-specific error
  text before delegating to `play_macro(...)`

## Validation

- `pytest -q tests/test_editor_macros_named.py tests/test_editor_prompt_completion_hostcalls.py -k macro tests/test_mxcontext.py tests/test_mkrevzip.py`
- `python tools/mxcontext.py --check`

# Rev638 — keep plain URL commands truthful before Enter

Plain `urlopen`, alias `openurl`, and `urlcopy` command-bar completion now reuse
one tiny under-cursor URL preview instead of falling back to generic command or
alias metadata.

## Why

Micromax already had the important runtime truth after Enter:

- `urlopen` already knew whether there was an under-cursor URL at all
- the open path already knew whether `cap.open-url` blocked opening
- the open path already knew whether `open-url.confirm` would interpose
- `urlcopy` already acted on that same exact URL without the capability gate
- `openurl` was already just an alias for `urlopen`

Leaving the exact no-arg command-bar rows generic right before execution hid the
one thing the user most needed to know: whether there is a concrete URL here,
and whether opening it is blocked or will ask for confirmation.

## What changed

- new shared `_current_url_preview_summary(...)` centralizes one tiny under-cursor URL witness
- new `_prompt_urlopen_command_row(...)` reuses that witness for both `urlopen` and `openurl`
- new `_prompt_urlcopy_command_row(...)` reuses the same witness for `urlcopy`
- exact command completion now previews `disabled (cap.open-url) · URL`, `URL [confirm]`, `URL`, or `no url under cursor`

## Focused tests

- `pytest -q tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_urlopen_command_previews_capability_blocked_current_url`
- `pytest -q tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_openurl_alias_previews_confirmed_current_url`
- `pytest -q tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_urlcopy_command_previews_current_url`
- `pytest -q tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_urlcopy_command_previews_typed_blocker`

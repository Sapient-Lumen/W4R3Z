# Rev639 — keep plain `buffers` and `marks` truthful before Enter

Plain `buffers` and `marks` command-bar completion now reuse one tiny live
inventory witness instead of falling back to generic command metadata.

## Why

Micromax already had the important runtime truth after Enter:

- `buffers` already reported a counted open-buffer inventory
- `marks` already reported a counted mark inventory
- `showbuffer` already reused one compact live buffer witness before Enter
- `showmark` already reused one compact live mark witness before Enter

Leaving the broad no-arg `buffers` and `marks` rows generic right before
execution hid the same current editor state their neighboring inspectors already
knew how to summarize.

## What changed

- new `_prompt_buffers_command_row(...)` routes plain `buffers` through `_buffer_inventory_preview_summary()`
- new `_prompt_marks_command_row(...)` routes plain `marks` through `_mark_inventory_preview_summary()`
- exact command completion now previews one concrete active/dirty buffer or mark anchor instead of generic command prose

## Focused tests

- `pytest -q tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_buffers_command_previews_live_inventory`
- `pytest -q tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_marks_command_previews_live_inventory`

# Rev633 — `helpnavpick` command preview keeps current docs navigation visible

## What changed

Plain `helpnavpick` now previews one tiny truthful summary of the current docs page before Enter.

The exact command-bar row reuses a shared `_helpnavpick_preview_summary()` helper, so it can show either:

- `N section(s), M help target(s) · Top: 1 | e.g. ...`
- `not in a docs buffer`

instead of collapsing back to generic command metadata.

## Why this matters

`helpnavpick` is the searchable current-doc navigator people reach for when they want to move around one page quickly without remembering whether the next useful target is a heading or a link. Micromax already knew that live page inventory through `help_nav_section_summary_rows()` and already surfaced it after Enter through `showhelpnav`, but the exact command row still hid that truth at the last moment before execution.

This tiny landing keeps the command bar aligned with the headless-first rule that the editor should show the live truth it already knows instead of making users or future LLMs infer it from neighboring commands.

## Implementation notes

- extended `_prompt_section_summary_rows_for_command(...)` so `helpnavpick` can reuse the same current-doc summary substrate as `showhelpnav`
- added `_helpnavpick_preview_summary()` for the tiny no-arg preview
- routed exact command-bar completion for plain `helpnavpick` through `_prompt_helpnavpick_command_row(...)`
- kept the blocker explicit as `not in a docs buffer`

## Verification

- `pytest -q tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_helpnavpick_command_previews_live_inventory tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_helpnavpick_command_previews_typed_blocker tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_helpback_command_previews_next_history_target tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_helphistory_command_previews_live_inventory tests/test_mxcontext.py::test_mxcontext_cli_can_emit_json_and_check_referenced_paths tests/test_mkrevzip.py::test_mkrevzip_embeds_context_manifest`
- live prompt spot-check of plain `helpnavpick` in a docs buffer and outside docs

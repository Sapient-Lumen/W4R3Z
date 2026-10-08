Rev634 note: plain `helpoutlinepick` now keeps current docs-heading inventory visible before Enter — the exact command-bar row reuses one tiny current-doc section summary, so it can show `N section(s), M headings ...` or `not in a docs buffer` instead of generic command metadata.

Why this tiny landing matters:
- `helpoutlinepick` is the narrowest current-page heading navigator people use when they already know they want a heading, not a mixed heading/link target.
- Micromax already had the truthful substrate: `help_outline_section_rows()` exposed grouped current-page heading inventory for scripts, `helpoutlinepick` already failed with `helpoutlinepick: not in a docs buffer`, and the command prompt already knew how to render exact command rows.
- The trust seam was only pre-Enter: plain `helpoutlinepick` still looked generic right when the user was deciding whether the current docs page had useful heading structure.

What changed:
- added shared `_help_doc_section_preview_summary(cmd, noun)` for tiny current-doc grouped previews
- added `_helpoutlinepick_preview_summary()` and `_prompt_helpoutlinepick_command_row(...)`
- taught `_prompt_section_summary_rows_for_command(...)` about `helpoutlinepick`
- routed exact command completion for `helpoutlinepick` through the same truthful preview path

Focused checks:
- `pytest -q tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_helpoutlinepick_command_previews_live_inventory tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_helpoutlinepick_command_previews_typed_blocker tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_helpnavpick_command_previews_live_inventory tests/test_mxcontext.py::test_mxcontext_cli_can_emit_json_and_check_referenced_paths tests/test_mkrevzip.py::test_mkrevzip_embeds_context_manifest`
- `python tools/mxcontext.py --check`

Future follow-on:
- keep scanning for the last exact docs-navigation commands whose no-arg command-bar rows still hide live state behind generic metadata

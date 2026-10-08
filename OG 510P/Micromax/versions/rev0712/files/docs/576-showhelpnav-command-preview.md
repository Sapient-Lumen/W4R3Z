Rev635 note: plain `showhelpnav` now keeps the no-docs blocker truthful before Enter — the exact command-bar row reuses the same tiny current-doc navigation summary substrate as `helpnavpick`, so it can show `not in a docs buffer` instead of the misleading fallback `0 section(s), 0 targets`.

Why this tiny landing matters:
- `showhelpnav` is the explicit grouped current-doc navigator summary, so people reach for it precisely when they want to know whether the current docs page is navigable at all.
- Micromax already had the truthful substrate: `showhelpnav` already failed with `showhelpnav: not in a docs buffer` after Enter, and `_help_doc_section_preview_summary(...)` already knew how to render blocker-aware current-doc grouped previews for nearby docs pickers.
- The trust seam was only pre-Enter: the exact command-bar row still reused the generic grouped-summary preview helper, which flattened no-docs state into a misleading zero-count summary.

What changed:
- added `_showhelpnav_preview_summary()` to reuse `_help_doc_section_preview_summary('showhelpnav', 'help target')`
- added `_prompt_showhelpnav_command_row(...)`
- routed exact command completion for `showhelpnav` through that blocker-aware helper instead of the generic grouped-summary row
- added focused prompt tests for both live current-doc inventory and the no-docs blocker

Focused checks:
- `pytest -q tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showhelpnav_command_previews_live_inventory tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showhelpnav_command_previews_typed_blocker tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showhelpnav_uses_helpnav_section_summary_metadata tests/test_editor_helpnavpick.py::test_helpnav_section_summary_rows_and_showhelpnav_are_count_aware tests/test_mxcontext.py::test_mxcontext_cli_can_emit_json_and_check_referenced_paths tests/test_mkrevzip.py::test_mkrevzip_embeds_context_manifest`
- `python tools/mxcontext.py --check`

Future follow-on:
- keep scanning the remaining grouped-summary command rows for blocker states that still flatten into generic zero-count previews before Enter

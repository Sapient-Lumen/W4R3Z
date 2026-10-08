# Rev637: `helplinkpick` command preview keeps current-doc link truth visible

## Why

`helplinkpick [QUERY]` already uses the current docs page's grouped link inventory after Enter. Before rev637, the exact command-bar row still fell back to generic command metadata right at the moment someone was deciding whether current-doc link navigation was even available.

That made the docs link-jump loop slightly less trustworthy than its siblings:

- `showhelplink` already previewed the exact current link or a typed blocker
- `helpfollow` / `helplinkcopy` / `helpcopylink` already previewed the same exact current-link truth before Enter
- `helpnavpick` already previewed grouped mixed heading/link inventory or `not in a docs buffer`
- `helpoutlinepick` / `helpjump` already previewed grouped heading inventory or the same blocker

`helplinkpick` should speak the same tiny honest dialect before Enter instead of hiding live current-doc link availability behind static prose.

## What changed

- taught `_prompt_section_summary_rows_for_command(...)` to resolve `helplinkpick` through `help_link_section_rows()`
- added `_helplinkpick_preview_summary()`
- added `_prompt_helplinkpick_command_row(...)`
- exact command-bar completion for plain `helplinkpick` now reuses `_help_doc_section_preview_summary('helplinkpick', 'link')`
- the row now shows either:
  - `N section(s), M links · ...`
  - `not in a docs buffer`

## Verification

Focused checks:

- `pytest -q tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_helplinkpick_command_previews_live_inventory`
- `pytest -q tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_helplinkpick_command_previews_typed_blocker`
- `pytest -q tests/test_editor_helplinkpick.py::test_helplinkpick_opens_link_target_doc tests/test_editor_helplinkpick.py::test_helplinkpick_requires_docs_buffer`
- `pytest -q tests/test_mxcontext.py::test_mxcontext_cli_can_emit_json_and_check_referenced_paths tests/test_mkrevzip.py::test_mkrevzip_embeds_context_manifest`

Direct sanity check:

- exact `helplinkpick` command-bar completion now previews the same grouped link inventory visible after Enter, including the typed blocker `not in a docs buffer` outside docs buffers.

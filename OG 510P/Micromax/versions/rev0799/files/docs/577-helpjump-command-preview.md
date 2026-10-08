# Rev636: `helpjump` command preview keeps current-doc heading truth visible

## Why

`helpjump [QUERY]` already uses the current docs page's heading inventory after Enter, and plain `helpjump` already opens the same heading-jump flow humans reach through `helpoutlinepick`. Before rev636, the exact command-bar row still fell back to generic command metadata right at the moment someone was deciding whether direct heading jumps were even available.

That made the docs jump loop slightly less trustworthy than its siblings:

- `helpoutlinepick` already previewed grouped heading inventory or `not in a docs buffer`
- `helpnavpick` already previewed grouped mixed heading/link inventory or the same blocker
- `showhelpnav` already previewed the same grouped current-doc navigation truth it would expose after Enter

`helpjump` should speak the same tiny honest dialect before Enter instead of hiding live current-doc heading availability behind static prose.

## What changed

- added `_helpjump_preview_summary()`
- added `_prompt_helpjump_command_row(...)`
- exact command-bar completion for plain `helpjump` now reuses `_help_doc_section_preview_summary('helpoutlinepick', 'heading')`
- the row now shows either:
  - `N section(s), M headings · ...`
  - `not in a docs buffer`

## Verification

Focused checks:

- `pytest -q tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_helpjump_command_previews_live_inventory`
- `pytest -q tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_helpjump_command_previews_typed_blocker`
- `pytest -q tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_helpjump_uses_exact_heading_metadata`
- `pytest -q tests/test_editor_helpjump.py::test_helpjump_without_args_opens_outline_prompt`
- `pytest -q tests/test_mxcontext.py::test_mxcontext_cli_can_emit_json_and_check_referenced_paths tests/test_mkrevzip.py::test_mkrevzip_embeds_context_manifest`

Direct sanity check:

- exact `helpjump` command-bar completion now previews the same grouped heading inventory visible through `helpoutlinepick`, including the typed blocker `not in a docs buffer` outside docs buffers.

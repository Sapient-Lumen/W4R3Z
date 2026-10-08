# Rev629 - `helpforward` command preview tells the truth

## What changed

Plain `helpforward` now previews the next docs-history replay target before
Enter instead of falling back to generic command metadata.

The exact command-bar row now reuses a tiny shared
`_helpforward_preview_summary()` helper, so it stays in the same typed dialect
as the runtime command and `help_navigation_model()`:

- `next TOPIC @ line:col`
- `next TOPIC @ line:col (+N)`
- `missing doc: TOPIC`
- `forward stack empty`

## Why this matters

Micromax already kept the docs replay loop inspectable after Enter:

- `helpforward` reopened the exact next page in forward history
- `help_navigation_model()` already exposed forward target/count/warning state
- `helpback` had just learned to keep its own replay target visible before Enter

That left one small split-truth seam: the forward replay command still looked
like generic command prose at exactly the moment a user or future LLM wanted to
know whether forward replay was ready, stale, or empty.

This change keeps the fix deliberately tiny and headless-first. It does not
change replay semantics. It only makes the command row surface the same truth
Micromax already knew.

## Files touched

- `src/micromax_editor/editor.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tools/mxcontext.py`
- `tests/test_mxcontext.py`
- `README.md`
- `TODO.md`
- `docs/01-llm-start-here.md`
- `docs/43-worklist.md`
- `docs/55-editor-command-bar.md`
- `docs/64-editor-prompt-completion.md`
- `docs/66-editor-micromax-commands.md`
- `docs/98-help-browser.md`

## Focused verification

- `pytest -q tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_helpforward_command_previews_next_history_target tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_helpforward_command_previews_empty_history tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_helpback_command_previews_next_history_target tests/test_mxcontext.py::test_mxcontext_cli_can_emit_json_and_check_referenced_paths tests/test_mkrevzip.py::test_mkrevzip_embeds_context_manifest`
- live prompt spot-check of plain `helpforward` after `helpback`

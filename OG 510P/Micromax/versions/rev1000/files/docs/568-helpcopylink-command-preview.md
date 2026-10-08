# Rev627 — keep plain `helpcopylink` truthful before Enter

## What changed

Plain `helpcopylink` command-bar completion now reuses the same tiny current-link
preview as `helplinkcopy`, `showhelplink`, and `helpfollow`.

That means the alias row now shows one of three real states instead of generic
alias metadata right before execution:

- `LABEL @topic [kind] -> target ...` for one resolved current docs link
- `no link under cursor`
- `not in a docs buffer`

## Why it matters

`helpcopylink` is intentionally tiny, but aliases are still part of the user
surface. Leaving the alias generic while the canonical copy action already told
the truth created one unnecessary trust gap for humans and future LLMs reading
command-bar state. This keeps the alias honest without adding any new logic
surface of its own.

## Implementation notes

- exact command-bar completion now routes both `helplinkcopy` and
  `helpcopylink` through `_prompt_helplinkcopy_command_row(...)`
- `_prompt_helplinkcopy_command_row(...)` still reuses
  `_current_help_link_preview_summary()`
- focused tests pin both live-link and typed-blocker alias previews

## Focused verification

- `pytest -q tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_helpcopylink_alias_previews_current_link`
- `pytest -q tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_helpcopylink_alias_previews_typed_blocker`
- `pytest -q tests/test_mxcontext.py::test_mxcontext_cli_can_emit_json_and_check_referenced_paths tests/test_mkrevzip.py::test_mkrevzip_embeds_context_manifest`

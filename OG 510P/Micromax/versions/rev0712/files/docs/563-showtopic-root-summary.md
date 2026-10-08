# Rev622 — `showtopic` root summary

Micromax already knew how to resolve one exact topic name through the same
precedence humans trust in `help NAME`: command, action, visible word, then doc.
That exact metadata was already visible once a name token existed in
`showtopic NAME`, and broader `showtopics [QUERY]` summaries already exposed the
catalog in grouped form. But the root `showtopic` path still hid that live truth
both before and after Enter.

This tiny landing keeps the no-arg exact inspector honest:

- plain command-bar `showtopic` now reuses `_topic_inventory_preview_summary()` before Enter
- raw runtime `showtopic` now prints the same summary before `usage: showtopic NAME`
- the shared helper prefers calmer doc/word samples before noisier command/action rows so the root witness stays legible

This is a small trust/flow cleanup. The goal is simple: the root exact topic
inspector can stay usage-shaped while still telling the truth about the live
help-topic catalog before it asks for one exact topic token.

Focused verification:

- `tests/test_editor_mx_commands_and_completion.py::test_showtopic_root_reports_runtime_summary_then_usage`
- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showtopic_command_previews_live_inventory`
- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showtopic_uses_generic_topic_metadata`
- `tests/test_mxcontext.py::test_mxcontext_cli_can_emit_json_and_check_referenced_paths`
- `tests/test_mkrevzip.py::test_mkrevzip_embeds_context_manifest`

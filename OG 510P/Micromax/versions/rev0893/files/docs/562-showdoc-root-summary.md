# Rev621 — `showdoc` root summary

## What changed

Plain `showdoc` is still the narrow exact docs-topic inspector, but its root
entry point no longer falls back to generic command prose at the moment a human
or future LLM most needs calm orientation.

Micromax now keeps one shared live docs-catalog witness on that path:

- plain command-bar `showdoc` reuses `_doc_inventory_preview_summary()` before Enter
- raw runtime `showdoc` now prints the same summary before `usage: showdoc TOPIC`
- the sample picker prefers calmer docs topics like `vision` over rev-churn handoff pages
- docs prompt metadata now reuses cached docs rows so exact `showdoc TOPIC` completion stays responsive

## Why it matters

This is a tiny trust/flow cleanup. Micromax already knew the visible docs
catalog through `doc_prompt_rows()`, `doc_detail_row(TOPIC)`, and broad
`showdocs [QUERY]` section summaries. But the narrowest exact docs inspector
still hid that truth both before and after Enter.

Keeping one compact witness visible means the root docs path can stay
usage-shaped while still saying what is actually available right now.

## Verification

Focused coverage pins both sides of the entry point:

- `tests/test_editor_help_docs_buffers.py::test_showdoc_root_reports_runtime_summary_then_usage`
- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showdoc_command_previews_live_inventory`
- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showdoc_and_help_docs_use_doc_metadata`

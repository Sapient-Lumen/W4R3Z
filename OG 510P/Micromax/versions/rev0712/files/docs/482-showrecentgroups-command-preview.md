# `showrecentgroups` command-bar preview (rev540)

## Why

Micromax already knew how to answer grouped recent-file questions through
`showrecentgroups [QUERY]` and the stable `recent_section_summary_rows(...)`
surface. Query-time completion for `showrecentgroups QUERY` already reused that
same grouped metadata too. But plain `showrecentgroups` in the command bar
still looked like a generic exact-command row right before Enter.

That was a small trust/flow seam: the grouped recent-file inspector already knew
how many visible project buckets existed and which one was first, yet the first
row humans and future LLMs saw hid that grouped truth until after execution.

## What changed

- new `Editor._prompt_showrecentgroups_command_row(...)` reuses
  `recent_section_summary_rows('')`
- exact command completion for plain `showrecentgroups` now keeps the ordinary
  command doc while replacing the generic hint with either:
  - `N section(s), M file(s) · latest ...`
  - `0 section(s), 0 file(s)`

## Example

With two visible project buckets, plain `showrecentgroups` can now preview as:

- `2 section(s), 2 file(s) · latest /tmp/demo: 1 | e.g. daily.txt #1 [active] @ 1:0 — notes/daily.txt | current buffer`

## Tests

- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showrecentgroups_command_previews_group_inventory`
- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showrecentgroups_command_previews_empty_inventory`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`

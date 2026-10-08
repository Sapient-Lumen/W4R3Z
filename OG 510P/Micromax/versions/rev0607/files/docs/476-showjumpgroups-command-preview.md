# `showjumpgroups` command-bar preview (rev534)

## Why

Micromax already knew the grouped jumplist buckets through `showjumpgroups [QUERY]`, `jump_section_summary_rows()`, and the newer `jumps` / `jumpback` / `jumpforward` command-row previews. But plain `showjumpgroups` in the command bar still looked like a generic no-arg command right before Enter.

That was a small trust/flow seam: the command existed precisely to inspect the current grouped `Current` / `Back` / `Forward` buckets, yet the command bar hid whether any such buckets were visible until after execution.

## What changed

- new `Editor._prompt_showjumpgroups_command_row(...)` reuses `jump_section_summary_rows('')`
- exact command completion for plain `showjumpgroups` now keeps the ordinary command doc while replacing the generic info hint with:
  - `0 section(s), 0 jump(s)` when the current buffer has no jumplist entries
  - `N section(s), M jump(s) · Current X · Back Y · Forward Z` when grouped buckets are visible

## Examples

- `showjumpgroups` with three visible buckets can preview as:
  - `3 section(s), 3 jump(s) · Current 1 · Back 1 · Forward 1`
- `showjumpgroups` with an empty register previews as:
  - `0 section(s), 0 jump(s)`

## Tests

- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showjumpgroups_command_previews_group_inventory`
- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showjumpgroups_command_previews_empty_inventory`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`

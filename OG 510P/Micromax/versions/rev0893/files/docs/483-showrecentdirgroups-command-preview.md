# `showrecentdirgroups` command-bar preview (rev541)

## Why

Micromax already knew the grouped recent-directory inventory through `showrecentdirgroups [QUERY]`, `ed.recent-dir-section-summary-rows`, and the adjacent exact `showrecentdir DIR|N|#N` surface. But plain `showrecentdirgroups` in the command bar still looked like a generic command row right before Enter.

That was a small trust/flow seam: the command existed precisely to expose the grouped parent-directory buckets, yet the command bar hid how many visible sections existed and which bucket anchored the top of the register until after execution.

## What changed

- new `Editor._prompt_showrecentdirgroups_command_row(...)` reuses `recent_dir_section_summary_rows('')`
- exact command completion for plain `showrecentdirgroups` now keeps the ordinary command doc while replacing the generic info hint with:
  - `N section(s), M file(s) · latest ...` when grouped recent-directory buckets exist
  - `0 section(s), 0 file(s)` when the recent register is empty

## Examples

- `showrecentdirgroups` with recent files under `src/` and `tests/` can preview as:
  - `2 section(s), 3 file(s) · latest /tmp/demo/tests: 2 | e.g. gamma.txt #1 [active] @ 1:0 — current buffer`
- `showrecentdirgroups` with an empty register previews as:
  - `0 section(s), 0 file(s)`

## Tests

- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showrecentdirgroups_command_previews_group_inventory`
- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showrecentdirgroups_command_previews_empty_inventory`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`

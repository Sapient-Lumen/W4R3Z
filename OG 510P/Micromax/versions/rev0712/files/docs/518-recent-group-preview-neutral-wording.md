# Neutral grouped recent-preview wording (rev576)

## Why

Rev575 already removed the misleading `latest ...` lead-in from several
grouped-summary command-bar previews, because those rows were describing the
first visible section, not a temporal event. But plain `showrecentgroups` and
`showrecentdirgroups` still carried the same old wording even though their
labels are project roots and parent directories, not time buckets.

That was a tiny trust/taste seam: Micromax already knew the exact grouped
recent-file section it was previewing, yet the first no-arg row still smuggled
in a false time axis right before Enter.

## What changed

- `Editor._prompt_showrecentgroups_command_row(...)` now reuses the shared
  `_prompt_section_summary_command_row(...)` helper
- `Editor._prompt_showrecentdirgroups_command_row(...)` now reuses the same
  helper too
- plain grouped recent previews now say `LABEL: N | e.g. ...` instead of
  `latest LABEL: N | e.g. ...`

## Examples

- `showrecentgroups` can now preview as:
  - `1 section(s), 2 file(s) · /tmp/demo: 2 | e.g. daily.txt #1 [active] @ 1:0 — notes/daily.txt | current buffer`
- `showrecentdirgroups` can now preview as:
  - `1 section(s), 2 file(s) · /tmp/demo/notes: 2 | e.g. beta.txt #1 [active] @ 1:0 — current buffer`

## Tests

- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showrecentgroups_command_previews_group_inventory`
- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showrecentdirgroups_command_previews_group_inventory`
- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_recent_group_commands_use_neutral_leading_section_previews`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`

# Rev620 — showrecentdir root summary stays truthful after Enter

## What changed

- added shared `Editor._recent_dir_inventory_preview_summary()`
- plain `showrecentdir` command-bar completion now reuses that shared summary
- raw runtime `showrecentdir` now prints `showrecentdir: ...` before `usage: showrecentdir DIR|N|#N`

## Why it matters

`showrecentdir DIR|N|#N` is the narrow exact inspector for one visible recent-directory bucket. The command bar already knew how to preview the newest visible bucket, but the raw runtime path still dropped straight to a generic usage line. That small mismatch made the no-arg entry point less trustworthy after Enter than before Enter.

Keeping one shared live summary on one tiny substrate means both surfaces now tell the same truth about the newest visible recent-directory bucket, including the visible slot, directory label, file count, active/open state, and one sample file witness.

## Focused checks

- `pytest -q tests/test_editor_buffer_mru_and_closeall.py::test_showrecentdir_root_reports_runtime_summary_then_usage tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showrecentdir_command_previews_latest_visible_bucket tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showrecentdir_command_previews_empty_inventory tests/test_mxcontext.py tests/test_mkrevzip.py`
- `python tools/mxcontext.py --check`

# Rev766 — save-conflict recovery and stat-cheap disk warnings

## Why this was risky

Rev765 made the disk write safer by default: atomic replacement, symlink-target preservation, and `save.checkexternal` refusal when a file changed on disk after open/save. That was the correct data-loss boundary, but it still left two user-facing trust gaps.

First, a stale save could say "no" without giving a direct recovery loop. Users needed explicit ways to inspect the conflict, reload from disk, or deliberately overwrite.

Second, the freshness model still conflated unknown/pathless state with "known missing." A buffer opened for a missing path could silently overwrite a file that another process created before the first save. Pure stat witnesses also miss some same-size/same-mtime changes on filesystems where timestamps can be restored or rounded.

While adding status visibility for those states, a waste risk appeared: content hashing is useful at a save boundary, but it should not run on every statusline render in a long-lived TUI/cloudtainer session.

## What changed

The save-conflict workflow is now explicit:

- `diff [N|--all]` shows a bounded unified diff of disk contents versus the current buffer.
- `diskdiff` is an alias for the same inspection path.
- `revert` reloads a clean path-backed buffer from disk.
- `revert!` discards local edits and reloads from disk, while recording an undo step for the discarded buffer text.
- `save! [FILE]` is the deliberate force-overwrite path.

`src/micromax_editor/file_recovery.py` owns the small recovery seam: decode a file in editor newline shape, detect line endings, and produce bounded disk-vs-buffer unified diffs.

The freshness vocabulary is stronger:

- `MISSING_FILE_SIGNATURE` distinguishes a path known to be absent from an unknown/pathless buffer.
- `disk_freshness_signature(...)` returns that sentinel instead of conflating missing with unknown.
- `EditorBuffer.disk_content_hash` records optional small-file content evidence alongside `disk_signature`.
- `save.checkexternal.hashmax` defaults to 1 MiB and lets the save boundary compare a BLAKE2b digest in addition to device/inode/size/mtime-ns.
- `save FILE` with the current file path now delegates to ordinary `save` instead of resetting the freshness witness as a save-as.
- Save-as to a missing target captures the target witness before commit and rechecks at write time, so a same-turn create race is refused and rolled back.

Status now exposes disk warnings without becoming the expensive guard:

- `status_model()` includes `disk_state`, `disk_summary`, `disk_changed`, `disk_missing`, `disk_known`, `disk_warning`, and `disk_error`.
- The default left statusline includes `$(disk)`, which renders warning states such as `[disk:changed]` or `[disk:missing]`.
- Status disk checks are intentionally stat-cheap. The stronger content digest is paid by save/check/recovery boundaries, not by every screen redraw.

## Prompt-ranking cleanup

Adding `diskdiff` exposed a fuzzy-ranking annoyance: typing `sk` could prefer the hidden middle substring in `diskdiff` over the obvious command-family match `showkey`. `prompt_rank.completion_fuzzy_sort_key(...)` now gives first-character matches priority before later contiguous substrings, so command-family prefixes stay practical without removing fuzzy matching.

## Remaining risk

There is still a time-of-check/time-of-use window between the freshness check and final `os.replace(...)`. Closing that fully would need a platform-specific compare-and-swap, advisory lock, backup, or merge workflow rather than another stat/hash check.

`save.checkexternal.hashmax` is deliberately bounded. Huge files are not hashed by default, and a user who lowers the hash budget after opening a file can reduce later same-stat detection until the next reload/save refresh.

The visible status disk state is intentionally stat-based. It can miss pathological same-stat content mutations before the next save attempt, but the save boundary still performs the stronger digest check when `save.checkexternal` and `save.checkexternal.hashmax` are enabled.

The next high-risk file-IO lane is script/hostcall parity: expose structured `ed.diff` / `ed.revert` style hostcalls, or make command-based script recovery examples canonical, so plugin/macro workflows do not need to parse human messages.

## Validation notes

Focused validation in this cloudtainer before packaging:

- `python -m py_compile src/micromax_editor/file_write.py src/micromax_editor/file_recovery.py src/micromax_editor/editor.py src/micromax_editor/command_dispatcher.py src/micromax_editor/statusformat.py src/micromax_editor/options_default.py src/micromax_editor/prompt_rank.py tools/mxdoctor.py tools/mxcontext.py tests/test_editor_fs_open_save.py tests/test_statusformat_templating.py tests/test_editor_statusline.py tests/test_prompt_rank.py` passed.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_editor_fs_open_save.py tests/test_statusformat_templating.py tests/test_editor_statusline.py tests/test_prompt_rank.py --durations=25` passed: 102 tests in 1.63 seconds.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_editor_mx_commands_and_completion.py tests/test_command_palette_path_completion.py tests/test_editor_prompt_completion_hostcalls.py --durations=20` passed: 342 tests in 17.41 seconds.
- `python tools/mxdoctor.py` passed: `mxlint` ok and 351 bounded preflight tests in 7.81 seconds.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_revision_index.py tests/test_mxcontext.py tests/test_mkrevzip.py tests/test_mxdoctor.py --durations=20` passed: 17 tests in 6.24 seconds.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_packaging_stdlib.py --durations=10` passed: 1 test in 10.20 seconds after rerunning a killed first invocation.
- `bash scripts/lint.sh` and `python tools/mxcontext.py --check` passed.
- `python tools/mxtest.py --plan --chunks 8 --strategy segment --json /mnt/data/micromax_rev0766_mxtest_plan_final.json` collected 1625 tests into chunk sizes 204, 203, 203, 203, 203, 203, 203, 203.

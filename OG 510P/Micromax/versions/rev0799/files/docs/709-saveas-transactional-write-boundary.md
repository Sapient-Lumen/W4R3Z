# Rev764 — transactional save-as and failed-save rollback

## Why this was risky

The file-write boundary is one of the highest-trust editor surfaces. A failed `saveas` should not rename the live buffer, steal marks, change MRU order, or point the active buffer at a different open file. Before this revision, `save FILE` / `saveas FILE` mutated the current buffer identity before the write succeeded. If the target path was already open, the fallback retitle path could even activate and save the already-open target buffer instead of the current buffer.

The ordinary save path had a related mutation-before-proof issue. Save cleanup options such as `rmtrailingws` and `eofnewline` were applied to the buffer and recorded as undo before encoding and writing. If encoding or the filesystem write failed, the command could leave unsaved cleanup edits and undo history behind even though the save failed.

## What changed

`src/micromax_editor/editor.py` now has a small `BufferIdentitySnapshot` plus `Editor.save_as(path)`:

- `save_as()` rejects empty targets and targets already represented by another open buffer or normalized open path.
- It snapshots the active buffer's name, path, local options, active-buffer pointer, buffer MRU, and marks before changing identity.
- It updates path/filetype and retitles the buffer only for the duration of the attempted save.
- Any exception restores the snapshot before surfacing the error.

`src/micromax_editor/command_dispatcher.py` now delegates both script and interactive save-as flows to `Editor.save_as(...)` instead of inlining path/name mutation in the command wrapper.

`Editor._save_buffer(...)` now proves more of the write before mutating the buffer:

- cleanup text is computed separately from the live buffer;
- file-format conversion and encoding happen before cleanup mutation;
- cleanup mutation and undo recording are rolled back if the later write raises;
- dirty, fastdirty, version, saved signature, and undo stack are restored on failed cleanup/write transitions.

## Concrete bugs fixed

- `saveas` to a path already open no longer saves or activates the wrong buffer.
- A failed pathless `saveas` no longer strands a `draft` buffer under the target path/name.
- Marks and buffer MRU are restored after a failed save-as.
- Encoding failures no longer trim trailing whitespace or append EOF newlines to the live buffer before raising.
- Failed cleanup/write transitions preserve clean fastdirty buffers as clean instead of leaving false dirty state behind.

## Regression coverage

`tests/test_editor_fs_open_save.py` now covers the collision, rollback, mark/MRU, failed-cleanup, and fastdirty-clean-state cases. `tools/mxdoctor.py` includes that file in the bounded preflight, so the file-write trust boundary is checked by the default doctor lane.

## Remaining risk

The write itself still uses the direct `Path.write_bytes(...)` path. This revision protects in-memory editor state around failed writes; it does not yet provide an atomic temp-file-and-replace write strategy for disk contents. The next high-value file-IO step is a configurable atomic-write path that preserves permissions where possible, handles cross-device and Windows semantics explicitly, and documents how much durability is promised.

## Validation notes

Focused validation in this cloudtainer after merging this with the plugin-unload rev764 lane:

- `python -m py_compile src/micromax_editor/editor.py src/micromax_editor/command_dispatcher.py tests/test_editor_fs_open_save.py tools/mxdoctor.py tests/test_mxdoctor.py` passed.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_editor_fs_open_save.py tests/test_mxdoctor.py --durations=15` passed: 40 tests in 1.21 seconds.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_editor_core.py tests/test_editor_buffer_lifecycle_recent.py tests/test_editor_help_docs_buffers.py tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_save_command_previews_pathless_buffer_and_saveas_hint tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_saveas_command_previews_current_path_and_expectation tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_saveas_command_previews_pathless_buffer --durations=20` passed: 96 tests in 3.24 seconds.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_editor_fs_open_save.py tests/test_mxdoctor.py tests/test_plugin_reload_recovery.py tests/test_plugin_json_schema.py tests/test_plugin_load_errors.py tests/test_plugin_hostcalls.py --durations=25` passed: 62 tests in 0.66 seconds.
- `python tools/mxdoctor.py` passed: `mxlint` ok and 285 bounded preflight tests in 7.02 seconds.
- `bash scripts/lint.sh` passed.
- `python tools/mxcontext.py --check` passed.
- `python tools/mxtest.py --plan --chunks 8 --strategy segment --json /mnt/data/micromax_rev0764_mxtest_plan.json` collected 1603 tests into segment chunks of 201, 201, 201, 200, 200, 200, 200, and 200 tests.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_packaging_stdlib.py --durations=10` passed: 1 test in 11.14 seconds.

This document records a second substantive rev764 audit/fix. `docs/708-plugin-unload-runtime-boundary.md` records the plugin lifecycle portion of the same revision. Full-suite evidence remains the explicit chunked `mxtest` lane; this revision does not claim a full-suite pass.

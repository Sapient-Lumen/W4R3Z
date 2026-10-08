# Rev767 — script file caps and structured recovery hostcalls

## Why this was risky

Rev766 gave humans a complete save-conflict loop: `diskdiff`, `revert`, `revert!`, and `save!`. The script/plugin surface still lagged behind it. Scripts could run command strings through `ed.command`, but structured recovery required parsing human messages or manually calling older hostcalls.

While wiring that parity, I found a more serious capability bug. In script context, `save` validated a relative buffer path against `cap.fs-root`, but the actual save call could still write that relative path against the process current working directory. A script-owned buffer with `path="in.txt"`, `cap.fs-root=/safe/root`, and cwd elsewhere could be approved as `/safe/root/in.txt` but write `./in.txt` instead. The legacy `ed.save` hostcall had the same pre-mutation problem.

## What changed

New module:

- `src/micromax_editor/file_scriptops.py`

It owns capability-checked file operations for scripted callers. It anchors relative paths under `cap.fs-root`, checks resolved paths for symlink escapes, and returns the nominal path to the editor so write operations can still preserve symlink identity after the trust check.

New module:

- `src/micromax_editor/file_hostcalls.py`

It installs structured recovery hostcalls:

- `ed.disk-state` → current buffer disk freshness map;
- `ed.diff` → `( max-lines -- ok lines err )` disk-vs-buffer diff rows;
- `ed.revert` → `( force -- ok info err )` reload current buffer from disk;
- `ed.save-info` → `( force -- ok info err )` save current buffer with structured save metadata;
- `ed.save-as-info` → `( path force -- ok info err )` transactional save-as with structured metadata.

The old `ed.save` hostcall keeps its existing `( -- ok err )` shape for compatibility, but it now delegates to the same cap-root-aware transactional helper instead of mutating `eb.buf.path` before save success.

The command path also changed. Scripted `ed.command "save"`, scripted `save FILE`, scripted `diff`, and scripted `revert` now route through the same capability helpers. When an effective path must change because `cap.fs-root` anchors a relative buffer path, save uses `Editor.save_as(...)` so failures still roll buffer identity back. Diff and revert can read from the anchored path without reading cwd by accident.

`fs_sandbox.nominal_path(...)` was added beside `resolve_path(...)`. The trust check still uses the resolved path, but filesystem operations that need to preserve a symlink path can use the nominal path after the check.

## Regression coverage

New regressions prove:

- scripted `ed.command "save"` anchors a relative buffer path under `cap.fs-root` and does not write cwd;
- legacy `ed.save` hostcall anchors the same case and preserves the two-value return shape;
- structured `ed.diff`, `ed.revert`, and `ed.save-info` return machine-readable rows/maps and do not mutate during diff;
- forced structured save overwrites intentionally and refreshes the save witness.

## Same-turn save commit guard

While validating the scripted recovery seam, I also tightened the lower file-write boundary. Rev766 checked disk freshness before preparing the save payload, but an external writer could still change the file after Micromax had written its temporary file and just before the final atomic replace. The writer now accepts a `FileFreshness` witness and rechecks it immediately before direct write or `os.replace(...)`. If the target changed, the save fails, removes the temp file, leaves the editor buffer dirty, and preserves the external file.

`FileStateSignature` now includes permission bits. That makes a chmod/change-mode race visible to ordinary `save` instead of silently overwriting with stale expectations. `save!` remains the explicit override for intentional overwrites.

Additional regressions prove:

- an atomic-save race after temp creation refuses before replace and cleans the temp file;
- a save-as create race rolls buffer identity back and preserves the newly-created external target;
- permission-mode changes since open/save are treated as external freshness conflicts.

## Remaining risk

The new structured recovery lane covers current-buffer file operations. It does not yet expose a multi-buffer conflict inventory, merge UI, or compare-and-swap kernel primitive for the time-of-check/time-of-use window before `os.replace(...)`.

The cap-root helper intentionally remains best-effort. It denies resolved symlink escapes, but it is not a sandbox substitute for hostile local users who can race directory entries between check and use.

The new pre-commit freshness recheck narrows the save race, but without OS-level locking there is still a final window between the last stat/hash check and `os.replace(...)`.

## Validation notes

Focused validation in this cloudtainer before packaging:

- `PYTHONPYCACHEPREFIX=/tmp/micromax_pycache python -m py_compile src/micromax_editor/fs_sandbox.py src/micromax_editor/file_scriptops.py src/micromax_editor/file_hostcalls.py src/micromax_editor/editor.py src/micromax_editor/command_dispatcher.py src/micromax_editor/micromax_bridge.py tests/test_editor_script_context_fs_caps.py tests/test_editor_fs_open_save.py` passed.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPYCACHEPREFIX=/tmp/micromax_pycache python -m pytest -q tests/test_editor_script_context_fs_caps.py tests/test_editor_fs_open_save.py --durations=20` passed: 65 tests in 1.89 seconds after the pre-commit writer regressions were added.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPYCACHEPREFIX=/tmp/micromax_pycache python -m pytest -q tests/test_editor_script_context_fs_caps.py tests/test_editor_fs_open_save.py tests/test_editor_fs_read.py tests/test_editor_fs_list.py tests/test_editor_fs_stat.py tests/test_editor_readonly_option.py tests/test_statusformat_hostcalls.py tests/test_plugin_hostcalls.py --durations=20` passed: 86 tests in 1.90 seconds.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPYCACHEPREFIX=/tmp/micromax_pycache python -m pytest -q tests/test_editor_prompt_completion_hostcalls.py tests/test_editor_mx_commands_and_completion.py tests/test_command_palette_path_completion.py --durations=20` passed: 342 tests in 18.16 seconds.
- `bash scripts/lint.sh` passed.
- `PYTHONPYCACHEPREFIX=/tmp/micromax_pycache python tools/mxdoctor.py` passed: 364 bounded preflight tests in 12.99 seconds after `tools/mxdoctor.py` was expanded to include the script-context filesystem-capability suite.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPYCACHEPREFIX=/tmp/micromax_pycache python -m pytest -q tests/test_revision_index.py tests/test_mxcontext.py tests/test_mkrevzip.py tests/test_mxdoctor.py --durations=20` passed: 17 tests in 12.34 seconds.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPYCACHEPREFIX=/tmp/micromax_pycache python -m pytest -q tests/test_packaging_stdlib.py --durations=10` passed: 1 test in 17.68 seconds.
- `PYTHONPYCACHEPREFIX=/tmp/micromax_pycache python tools/mxtest.py --plan --chunks 8 --strategy segment --json /mnt/data/micromax_rev0767_mxtest_plan.json` collected 1637 tests into chunks `205, 205, 205, 205, 205, 204, 204, 204` with source digest `b3507b0bda9d`.


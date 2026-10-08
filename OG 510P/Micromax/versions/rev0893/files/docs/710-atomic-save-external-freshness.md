# Rev765 — atomic save and external-change guard

## Why this was risky

Rev764 stopped save/save-as from leaving the in-memory buffer half-renamed or half-cleaned when a write failed, but the actual disk write still used a direct target-path write. That left two high-trust editor failures open:

- a crash or write error during a direct write could leave the target path truncated or partially replaced;
- a buffer opened from disk could silently overwrite another process's newer file contents because Micromax had no saved on-disk freshness witness.

Those are more dangerous than another picker/registry cleanup because they can lose user data while still reporting an ordinary save path.

## What changed

`src/micromax_editor/file_write.py` is now the editor file-write seam. It owns:

- `write_file_bytes(...)`;
- same-directory temporary-file creation;
- `os.replace(...)` commit for the atomic save path;
- best-effort existing permission-bit preservation;
- optional file and parent-directory fsync;
- symlink-target preservation so atomic save updates the pointed-to file instead of replacing the visible symlink with a regular file;
- `file_state_signature(...)`, a small on-disk freshness witness based on device, inode, size, and mtime-ns.

The save path now has four save-specific options:

- `save.atomic` defaults to `true` and selects the atomic temp-file/replace path;
- `save.preserveperm` defaults to `true` and carries forward existing permission bits when replacing an existing file;
- `save.fsync` defaults to `false` and enables the heavier durability path;
- `save.checkexternal` defaults to `true` and refuses to save an opened buffer when the file changed on disk since open/save.

`EditorBuffer` now carries `disk_signature`. `open_file(...)` refreshes it after reading a file, `save(...)` refreshes it after a successful write, `save_as(...)` rollback restores it, and macro replay snapshots preserve it.

## Concrete bugs fixed

- A failed atomic replace leaves the old target file intact and removes the temporary file.
- Failed replace after save-cleanup still restores buffer text, dirty state, version, and undo depth.
- Existing POSIX permission bits are preserved through atomic replacement.
- Saving a path that is itself a symlink keeps the symlink and updates the target file.
- Saving a buffer whose file changed externally is refused by default.
- Operators can still intentionally overwrite external changes with `setlocal save.checkexternal false`.

## Remaining risk

This is a pragmatic editor save transaction, not a formal filesystem transaction. The atomic promise is limited to the final replacement step that the host OS provides, and `save.fsync` is off by default because durability syncs are slower and platform-dependent. The freshness witness is also a stat-based guard, so it can miss pathological cases where a filesystem reports unchanged size and mtime-ns after external mutation.

The next file-IO risk lane should be user-facing recovery: better conflict messaging, a `reload`/`diff`/`save!` workflow, and clear TUI status when a clean buffer has gone stale on disk.

## Validation notes

Focused validation in this cloudtainer:

- `python -m py_compile src/micromax_editor/file_write.py src/micromax_editor/editor.py src/micromax_editor/options_default.py tools/mxcontext.py tests/test_editor_fs_open_save.py` passed.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_editor_fs_open_save.py --durations=25` passed: 39 tests in 1.29 seconds.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_editor_fs_open_save.py tests/test_editor_buffer_lifecycle_recent.py tests/test_editor_core.py tests/test_editor_readonly_option.py tests/test_editor_prompt_completion_hostcalls.py --durations=25` passed: 383 tests in 8.06 seconds.

- `python tools/mxdoctor.py` passed: 293 bounded preflight tests in 14.20 seconds.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_revision_index.py tests/test_mxcontext.py tests/test_mkrevzip.py tests/test_mxdoctor.py --durations=20` passed: 17 tests in 11.87 seconds.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_packaging_stdlib.py --durations=10` passed: 1 test in 19.40 seconds.
- `bash scripts/lint.sh` and `python tools/mxcontext.py --check` passed.
- `python tools/mxtest.py --plan --chunks 8 --strategy segment --json /mnt/data/micromax_rev0765_mxtest_plan.json` collected 1611 tests into chunk sizes 202, 202, 202, 201, 201, 201, 201, 201.

## Rev766 follow-up

Rev766 implements the user-facing recovery lane called out above: `diff`/`diskdiff`, `revert`, `revert!`, and `save!` now give operators direct conflict choices. It also keeps the stronger content-hash freshness check on the save boundary while making visible status disk warnings stat-cheap, so long-running TUI redraws do not repeatedly hash open files.

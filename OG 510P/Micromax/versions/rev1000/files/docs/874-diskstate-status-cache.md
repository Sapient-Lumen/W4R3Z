# Rev874 / rev0916 — disk-state status cache

## Why this pass

Rev0915 deliberately avoided spawning one filesystem worker per status render.
That was the right waste avoidance, but it left a smaller hot-path problem:
`status_model()` still synchronously probed disk state and OS writability every
render for path-backed buffers.  On a fast local filesystem this is cheap; on a
remote, stalled, or unusual filesystem it is still an avoidable render-loop
host effect.

The online check kept the boundary narrow.  Python documents subprocess timeout
behavior as kill-and-wait cleanup, which remains appropriate for save/read/list
workers, but it is too expensive for a per-frame statusline.  Python also
explicitly documents `os.scandir()` as a closable context-managed iterator,
reinforcing that even observational filesystem iteration owns resources.
OWASP API4:2023 continues to name missing execution timeouts and resource limits
as a resource-consumption risk.  The local conclusion: do not create status
workers; cache hot observational status and keep explicit recovery commands live.

Research references:

- https://docs.python.org/3/library/subprocess.html
- https://docs.python.org/3/library/os.html#os.scandir
- https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/

## What changed

`src/micromax_editor/options_default.py` adds `diskstate.cachems` with a default
of `250`.  This is a tiny render-loop cache window for stat-only disk-state and
OS-level readonly checks.  Setting it to `0` restores fully live status probes.

`src/micromax_editor/editor.py` adds an ephemeral `EditorBuffer.disk_state_cache`,
`Editor.invalidate_disk_state_cache()`, `_disk_state_cache_seconds()`, and a
cached `_status_file_readonly()` helper.  `status_model()` now uses cached
`buffer_disk_state()` and cached OS readonly truth, so repeated statusline/screen
renders do not hit the filesystem once per frame.  Save/open/revert witness
refresh clears the cache.

`Editor.disk_state_rows()` and script/capability disk-state hostcalls pass
`refresh=True`, so explicit recovery inventory remains live instead of waiting
for the status cache to expire.

While auditing that path, one forgotten script-save preflight surfaced:
`save_current_buffer_under_caps()` still checked `nominal.exists()/is_dir()`
before entering the editor save boundary.  It now uses `ed._bounded_fs_stat(...)`
with the active `cap.fs-root` containment root.

A related command-palette drill-down probe now uses `_bounded_fs_stat(...)` too,
rather than a direct `Path.exists()/is_dir()` check after filesystem-list
capability has been granted.

## Validation

Focused validation passed:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_editor_fs_open_save.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_editor_script_context_fs_caps.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_command_palette_path_completion.py tests/test_editor_mx_commands_and_completion.py::test_ed_command_palette_hostcall_live_refresh_and_submit_action tests/test_editor_mx_commands_and_completion.py::test_commandpick_submit_on_command_opens_command_bar_with_prefill
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mxaudit.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxlint.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxaudit.py --check --limit 5
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxcontext.py --check
```

The first broad combined pytest lane for the three largest focused files hit the
outer cloudtainer timeout after partial progress, so this revision keeps its
claim to the split lanes above rather than calling it a full release run.

## Remaining risk

This is a cache/cadence fix, not asynchronous filesystem observation.  A status
refresh can still block when the cache expires.  The next stronger design would
move status disk observation into a slow explicit refresh loop or background
poller with stale markers, but that would require more UI/lifecycle policy than
this pass should take on.

Filesystem resource audit checks are also still hand-coded in `tools/mxaudit.py`.
The next non-bureaucratic version of that work should generate one filesystem
effect slice from a compact table instead of adding one more string predicate by
hand.

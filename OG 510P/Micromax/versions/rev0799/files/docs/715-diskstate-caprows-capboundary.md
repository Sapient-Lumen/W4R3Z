# Rev768 — disk-state rows, script capability boundaries, and plugin VM stack isolation

## Why this was risky

Rev767 added structured file-recovery hostcalls, but the active-buffer `ed.disk-state` shape was not enough for a real recovery dashboard. Operators need to see all buffers that are stale, missing, or otherwise risky before deciding whether to save, revert, or force-save.

The dangerous part was how easy it would be to expose that inventory to scripts by simply calling `Editor.disk_state_rows(...)`. That helper is appropriate for the interactive user command path, but it stats buffer paths directly. A script-visible multi-buffer disk inventory would therefore become an ambient filesystem-existence oracle unless it reused the `cap.fs-stat` / `cap.fs-root` boundary.

A second audit pass found a different runtime-trust leak: plugin source and lifecycle words could leave ordinary VM stack data behind. Plugin code is allowed to define words and register editor surfaces, but plugin load/reload/unload hooks are not a data-return API. Letting hook junk remain on the shared VM stack makes later script/plugin failures much harder to reason about.

## What changed

`src/micromax_editor/file_scriptops.py` now owns capability-gated disk-state helpers alongside the existing save/diff/revert script helpers:

- `disk_state_under_caps(ed)` returns the active buffer state without ambient stat access.
- `disk_state_rows_under_caps(ed, include_fresh=False)` returns rows shaped as `[name state warning changed missing dirty active path error]`.
- Path-backed rows require `cap.fs-stat` before any stat-like check.
- Relative path-backed rows are anchored through `cap.fs-root` before checking disk state.
- Unauthorized rows are represented as warning rows instead of raising, so dashboards can show the problem without scraping exceptions.

`src/micromax_editor/command_dispatcher.py` now routes scripted `diskstate [--all]` through `disk_state_rows_under_caps(...)`. The interactive command still uses `Editor.disk_state_rows(...)` so humans keep the direct recovery inventory they expect.

`src/micromax_editor/file_hostcalls.py` now exposes structured multi-buffer inventory:

```forth
ed.disk-states  ( include-all -- rows )
ed.disk-rows    ( include-all -- rows )  \ alias
```

`src/micromax_editor/micromax_bridge.py` adds the stdlib bridge word:

```forth
disk-states ( include-all -- rows )
```

## Mxtest checkpoint atomicity side fix

The rev768 heartbeat/checkpoint work made interrupted aggregate runs more observable, but the JSON writer itself still needed a small trust boundary. `tools/mxtest.py::write_json_summary(...)` now writes manifests through a same-directory temporary file, flushes and fsyncs that file, and then promotes it with `os.replace(...)`.

That means an aggregate checkpoint update should leave either the previous complete JSON manifest or the next complete JSON manifest. A failed replace no longer risks clobbering the only resume witness, and temporary files are cleaned up on the failure path.

## Prompt completion side fix

Adding `diskstate` and `diskconflicts` exposed a command-completion regression: fuzzy query `sst` stopped uniquely completing to `showstatus` because `diskstate` also contains the same characters as a later hidden subsequence. The fuzzy fallback now keeps only the best start-at-candidate band when such a band exists, so obvious command-family abbreviations remain useful while hidden-substring matching still works when there is no better family match.

## Plugin stack isolation side fix

`src/micromax_editor/plugin_runtime.py` now has a small `VmExecutionSnapshot` for stack-like execution state: data stack, return stack, call stack, and locals stack.

`src/micromax_editor/plugins.py` snapshots/restores that state around plugin source evaluation and lifecycle word execution. Definitions, wordlists, commands, hooks, timers, and other plugin registration side effects are still governed by the existing runtime registration transaction path; this new snapshot only prevents ordinary stack junk from leaking out of plugin source/init/deinit execution.

## Regression coverage

New and expanded tests cover:

- `ed.disk-state` refusing path-backed stats without `cap.fs-stat`;
- `ed.disk-states` / `ed.disk-rows` returning unauthorized warning rows rather than silently statting;
- relative disk-state rows using `cap.fs-root` instead of process cwd;
- scripted `ed.command "diskstate --all"` using the capability-gated row helper;
- the human `diskstate` command listing changed/missing buffers;
- plugin source/load failure not leaking stack junk;
- plugin init/reload/deinit hooks not leaving stack junk behind;
- atomic mxtest JSON writes leaving no temp files and preserving the old manifest on replace failure;
- command fuzzy completion preserving the obvious `showstatus` abbreviation after adding disk-state commands.

## Remaining risk

The row shape is intentionally plain and compact. It is enough for hostcalls, command output, and future UI dashboards, but it is not yet a richer recovery panel with per-row actions.

Atomic JSON replacement improves resume evidence, but it cannot defend against every host/filesystem failure mode; the full-evidence lane should still keep manifests outside fragile scratch paths when possible.

The plugin stack snapshot protects stack-like execution containers. It is not a full VM transaction and deliberately does not roll back successful definitions or editor registrations; those are handled by the plugin runtime registration machinery added in earlier revisions.

## Validation notes

Focused validation in this cloudtainer before packaging:

- `python -m py_compile src/micromax_editor/file_scriptops.py src/micromax_editor/file_hostcalls.py src/micromax_editor/command_dispatcher.py src/micromax_editor/editor.py src/micromax_editor/plugin_runtime.py src/micromax_editor/plugins.py tests/test_editor_script_context_fs_caps.py tests/test_editor_fs_open_save.py tests/test_plugin_reload_recovery.py` passed.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_editor_script_context_fs_caps.py tests/test_editor_fs_open_save.py tests/test_plugin_reload_recovery.py tests/test_mxtest.py --durations=20` passed: 162 tests.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_editor_prompt_completion_hostcalls.py tests/test_command_palette_path_completion.py tests/test_editor_mx_commands_and_completion.py tests/test_mxdoctor.py --durations=20` passed: 351 tests.
- `timeout 120s env PYTHONPYCACHEPREFIX=/tmp/micromax_pycache python tools/mxdoctor.py` passed with `452 passed in 22.29s` in the bounded preflight lane.

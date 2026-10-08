# Rev0922 — project-root marker batch

## What changed

Project-root grouping now observes parent marker files through one bounded batch stat pass instead of calling direct `Path.exists()` probes for every row and every parent directory.

`src/micromax_editor/editor.py` adds:

- `PROJECT_ROOT_MARKERS`
- `PROJECT_ROOT_MAX_DEPTH`
- `PROJECT_ROOT_CACHE_TTL_SECONDS`
- `PROJECT_ROOT_MARKER_BATCH_LIMIT`
- `_seed_project_root_cache()`
- `_project_root_cache_get()` / `_project_root_cache_put()`

The hot recent-file and buffer grouping paths seed the project-root cache before they sort/group rows.  Individual `_project_root_for_path()` calls still work, but they now populate the same short-lived cache through `stat_paths_contained_bounded()` with the existing filesystem stat timeout.  The cache is intentionally small and short-lived: it prevents one render from multiplying marker probes, but it is not a durable project index and will naturally age out if `.git`, `pyproject.toml`, or similar markers change during a session.

## Why this was next

Rev0921 bounded docs/help catalog scanning, but its own handoff named `_project_root_for_path()` as the next exact survivor.  This helper is not a broad recursive scanner, yet it sits in hot picker/status surfaces: recent files, grouped recent-file hostcalls, buffer grouping, section summaries, and prompt display all ask for the same root label repeatedly.

The old shape was small but wasteful:

1. normalize a file path,
2. decide file-versus-directory with a direct filesystem probe,
3. walk up to eight parents,
4. test six markers per parent with direct `exists()` calls,
5. repeat the same work for the label and display rewrite of the same row.

The new shape keeps the behavior but moves it into the existing bounded filesystem-observation family: one parent-marker batch for the visible rows, one short TTL cache, and no direct marker `Path.exists()` loop inside `_project_root_for_path()`.

## Online research used

- Python's `subprocess` documentation says timeout handling kills and waits for the child process, while process creation itself may not be interruptible on all platforms. That continues to support process-owned timeout seams for host work that can block.
- Python's `concurrent.futures` documentation documents ThreadPoolExecutor deadlock risks and cancellation limits for already-running work, which reinforces avoiding thread-pool cancellation as the containment story for filesystem probes.
- OWASP API4:2023 classifies missing execution timeouts and missing record/operation limits as unrestricted resource-consumption risk. Project-root grouping is not an HTTP API, but a picker surface that repeatedly observes dozens of marker paths has the same missing-limit shape.
- VS Code's Workspace Trust and extension-host docs continue to be a useful product comparison: workspace-derived behavior should not be able to silently expand the cost or authority of routine UI surfaces.

Sources: <https://docs.python.org/3/library/subprocess.html>, <https://docs.python.org/3/library/concurrent.futures.html>, <https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/>, <https://code.visualstudio.com/api/extension-guides/workspace-trust>, <https://code.visualstudio.com/api/advanced-topics/extension-host>.

## Tests and audit

New focused regressions in `tests/test_editor_buffer_lifecycle_recent.py` cover direct project-root discovery through the bounded marker batch and recent-project grouping cache reuse.  `tools/mxaudit.py --check` now hard-checks `project_root_marker_batch_boundary`, including the absence of the previous direct marker `exists()` loop.

Focused validation run for this revision:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_editor_buffer_lifecycle_recent.py::test_project_root_detection_uses_bounded_marker_batch tests/test_editor_buffer_lifecycle_recent.py::test_recent_project_rows_seed_project_root_cache_once
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_editor_buffer_lifecycle_recent.py::test_recentpick_groups_rows_by_project_root_and_rewrites_details tests/test_editor_buffer_mru_and_closeall.py::test_showrecentgroups_project_root_bucket_omits_duplicate_filename_echo tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showrecentgroups_project_root_bucket_omits_duplicate_filename_echo
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mxaudit.py::test_mxaudit_json_reports_repeatable_structural_signals tests/test_mxaudit.py::test_mxaudit_human_output_names_major_pressure_surfaces
PYTHONPATH=src python tools/mxaudit.py --check
```

## Remaining risk

This is still best-effort project labeling, not a full workspace index.  It can be killed after the configured stat timeout, but process creation itself can still take nonzero time.  The bounded marker batch intentionally follows the existing filesystem stat containment root; labels may be absent when markers sit outside the allowed root or when the marker batch budget is exhausted.

The next useful pass should keep the same concrete-retirement discipline: sweep another real direct filesystem or process survivor, or compact duplicated timeout evidence into living contracts only after a code seam is actually retired.

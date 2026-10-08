# Rev0915: save preflight timeout boundary

## Why this was next

Rev0914 made the atomic write commit killable, but the save path could still spend accepted host time before the writer process owned target-temp cleanup.  The risky survivors were not doctrine gaps: they were concrete filesystem calls in the data-loss lane.

The priority order for this pass was:

1. keep real target writes safe;
2. bound pre-save checks that can block before commit;
3. avoid a worker per status render or visible palette row;
4. leave direct/non-atomic writes in-process until a journaled design exists.

The online check reinforced that process-owned work is the usable recovery boundary here.  Python documents subprocess timeouts as kill/wait cleanup points, while Python discussions keep repeating that a running thread cannot be forcibly stopped reliably.  OWASP API4:2023 also keeps execution-time and resource ceilings in the core unrestricted-resource-consumption risk set.

## What changed

`src/micromax_editor/file_write.py` adds two save-preflight workers:

- `capture_file_freshness_bounded(...)` runs save-time stat plus optional small-file content digest capture in a killable process and raises `FileFreshnessTimeoutError` on timeout.
- `ensure_parent_directory_bounded(...)` runs `mkparents` parent creation in a killable process and raises `FileMkparentsTimeoutError` on timeout.

`src/micromax_editor/editor.py` now uses the bounded stat seam for the save target directory check instead of direct `Path.exists()/is_dir()`.  When `save.checkexternal` or disk witness refresh needs a freshness capture, `_capture_disk_freshness()` uses the new freshness worker if the VM has a positive `editor_file_freshness_timeout_seconds` budget.  It intentionally does **not** use that worker for the stat-only `buffer_disk_state()` status path, because status model rendering can be hot and should not spawn a process per screen refresh.

When `mkparents` is enabled, `_save_buffer()` now calls `ensure_parent_directory_bounded(...)` with the VM-tunable `editor_file_mkparents_timeout_seconds` budget.  A killed `mkparents` worker may leave parent directories that it already created, but it does not partially write the target file.  That is an acceptable failure mode for this convenience surface and is safer than killing a direct writer after truncation.

`src/micromax_editor/hostcall_boundary.py` adds:

- `DEFAULT_FILE_FRESHNESS_TIMEOUT_SECONDS`
- `DEFAULT_FILE_MKPARENTS_TIMEOUT_SECONDS`
- `effective_file_freshness_timeout_seconds()`
- `effective_file_mkparents_timeout_seconds()`

`src/micromax_editor/micromax_bridge.py` installs the matching VM attributes.  `tools/mxaudit.py` now hard-checks `editor_save_freshness_timeout_boundary` alongside the existing atomic-write boundary.

## What deliberately did not change

This pass did not wrap every status/disk-state probe in a worker.  `buffer_disk_state()` is called by the screen/status model, so a default timeout worker there would turn ordinary rendering into process churn.  That should be solved with caching or a slower explicit disk-state refresh cadence, not by blindly spawning per render.

This pass also did not make `save.atomic=false` killable.  The rev0914 rationale still holds: a process kill in that lane can leave the actual target partially written.

## Validation

Focused new tests passed:

```bash
PYTHONPATH=src pytest -q \
  tests/test_editor_fs_open_save.py::test_save_freshness_capture_timeout_kills_worker \
  tests/test_editor_fs_open_save.py::test_save_passes_vm_tunable_freshness_timeout_for_checkexternal \
  tests/test_editor_fs_open_save.py::test_save_directory_preflight_uses_bounded_stat \
  tests/test_editor_fs_open_save.py::test_mkparents_timeout_kills_worker_before_target_write \
  tests/test_editor_fs_open_save.py::test_save_passes_vm_tunable_mkparents_timeout \
  tests/test_editor_fs_open_save.py::test_atomic_file_writer_timeout_kills_worker_and_cleans_temp \
  tests/test_editor_fs_open_save.py::test_save_passes_vm_tunable_atomic_write_timeout \
  tests/test_mxaudit.py
```

Result: 9 passed.

Broader focused validation for this pass:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q \
  tests/test_editor_fs_open_save.py --durations=10
```

Result: 77 passed.

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q \
  tests/test_editor_script_context_fs_caps.py \
  tests/test_editor_persistence_cap_persist.py \
  tests/test_editor_fs_stat.py \
  tests/test_editor_fs_read.py \
  tests/test_editor_fs_list.py \
  --durations=10
```

Result: 110 passed.

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q \
  tests/test_mxaudit.py \
  tests/test_mxcontext.py \
  tests/test_revision_index.py \
  tests/test_docs_living_hygiene.py::test_repo_map_aggregate_lane_matches_makefile_defaults
PYTHONPATH=src python tools/mxaudit.py --check
PYTHONPATH=src python tools/mxcontext.py --json --check >/tmp/micromax_rev0915_context2.json
PYTHONPATH=src python tools/mxlint.py
```

Result: 9 passed; audit/context/lint passed.

`tools/mxtimely.py` also produced an OK summary for context, audit, lint, portability, and doctor in `.artifacts/mxtimely-summary.json` with rev0915.  This is still a split focused lane, not a full release-suite claim.

## Remaining risk

The save lane is now much better bounded, but not perfect:

- direct/non-atomic writes remain intentionally unkillable;
- status/disk-state stat checks remain synchronous to avoid process churn;
- killed `mkparents` workers can leave already-created directories;
- worker process creation itself can be delayed by the host before the timeout is observed;
- filesystem resource audit predicates are still hand-coded rather than generated from a small data table.

The next code-forward pass should choose between a tiny generated filesystem-effect table and a status/disk-state cache.  The cache is probably the more practical product improvement; the table is the better anti-regression tool.

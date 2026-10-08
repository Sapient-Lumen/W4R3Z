# Rev877 / rev0919 — status access bounded

## Why this pass

Rev0918 removed the per-row command-palette stat trap, but the exact single-path
sweep still found two small survivors in user-facing paths: parsecursor checked
whether a colon-containing literal path existed with a direct stat helper, and
the hot status read-only cue refreshed with `Path.exists()`, `Path.is_dir()`, and
`os.access()` when its cache expired.  Those are not large features, but they
are exactly the kind of leftover ambient filesystem probes that become hard to
find once the obvious read/list/write seams are fixed.

The online check kept this narrow: Python documents subprocess/process timeout
semantics as the enforceable kill/wait boundary, while thread-style cancellation
remains the wrong shape for blocking host I/O.  OWASP API4:2023 continues to
frame missing execution and resource limits as resource-consumption risk.  WASI
capability notes remain useful background for the longer-term host contract, but
this pass deliberately did not add a registry layer; it retired two direct probes
now.

Research references:

- https://docs.python.org/3/library/subprocess.html
- https://docs.python.org/3/library/concurrent.futures.html
- https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- https://github.com/WebAssembly/WASI/blob/main/docs/Capabilities.md

## What changed

`src/micromax_editor/file_access.py` adds `ContainedAccessResult`,
`access_path_contained()`, and `access_path_contained_bounded()`.  The helper is
a status-observation sibling of bounded stat: it binds existence/kind to the
opened fd when possible, keeps the write-access probe inside the same killable
filesystem worker when a positive stat timeout is configured, and returns a
small `exists/kind/writable` witness rather than making authorization decisions.

`src/micromax_editor/editor.py` now uses the bounded stat seam for parsecursor's
colon-containing literal-path check, preserving the existing behavior for real
files like `notes:archive` without doing a direct unbounded `stat_path_contained()`
from the parser.  Hot command-palette parsecursor checks reuse already-preseeded one-build
palette stat cache entries instead of spawning a single-path worker from row
rendering or query classification.  The status
read-only refresh now resolves through the filesystem sandbox helpers and calls
`access_path_contained_bounded()` instead of refreshing with direct
`Path.exists()`, `Path.is_dir()`, and `os.access()`.  The short stale/read-only
status cache remains unchanged; this pass only changes the live refresh seam.

`tools/mxaudit.py` adds `status_readonly_parsecursor_bounded`, which checks for
the new access worker, the parsecursor bounded-stat call, and the regressions
that keep the old direct stat/access shapes retired.

## Validation

Focused validation passed:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q \
  tests/test_editor_fs_open_save.py::test_parsecursor_existing_literal_path_uses_bounded_stat \
  tests/test_editor_fs_open_save.py::test_parsecursor_palette_literal_check_uses_preseeded_stat_cache \
  tests/test_editor_fs_open_save.py::test_open_file_parsecursor_places_cursor_when_enabled \
  tests/test_editor_fs_open_save.py::test_open_file_parsecursor_line_only_defaults_to_column_zero \
  tests/test_editor_fs_open_save.py::test_status_readonly_refresh_uses_bounded_access_probe \
  tests/test_editor_fs_open_save.py::test_disk_state_rows_refreshes_even_when_status_cache_is_warm \
  tests/test_command_palette_path_completion.py::test_command_palette_parsecursor_directory_open_row_still_drills_down \
  tests/test_command_palette_path_completion.py::test_command_palette_openpath_submit_reports_landed_target \
  tests/test_command_palette_path_completion.py::test_known_path_completion_candidates_reuse_batched_stat_cache
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_editor_fs_stat.py tests/test_mxaudit.py tests/test_revision_index.py tests/test_docs_living_hygiene.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxlint.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxcontext.py --check
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxaudit.py --check --limit 5
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mxaudit.py tests/test_revision_index.py tests/test_docs_living_hygiene.py
```

One broad combined command hit the outer cloudtainer timeout after completing
the focused pytest, `mxlint`, and `mxcontext` portions, so the audit/doc lanes
were rerun separately.  A later full command-palette-file lane also exceeded the
outer timeout in this cloudtainer, so the parsecursor/palette edge tests were
validated individually.  This is not a full release-suite claim.

## Remaining risk

`access_path_contained_bounded()` is intentionally status truth, not a write
permission authority.  It answers only whether status should show a path-backed
buffer as OS-read-only.  Save still owns the real write/freshness/conflict
boundaries.

Exact single-path UI helpers should continue to be swept, especially project-root
markers and help/plugin discovery paths.  The rule remains: fix hot or delayed
ambient probes before generating another broad policy table.

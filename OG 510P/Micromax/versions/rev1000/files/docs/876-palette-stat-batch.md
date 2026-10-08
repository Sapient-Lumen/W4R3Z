# Rev876 / rev0918 — palette stat batch

## Why this pass

Rev0917 made status disk observation stale-marked and throttled, but the command
palette still had a smaller version of the same waste pattern: recent-file and
known-path rows could ask for disk truth one visible path at a time.  Switching
that path to one worker per row would have bounded each row while multiplying
process churn in a hot picker surface.

The online check kept the fix in the same direction as the previous resource
passes.  Python's subprocess timeout contract is still the enforceable
kill/wait boundary for work that can block, while Python discussion around
executor cancellation reinforces that already-running thread work is not a
clean cancellation boundary.  OWASP API4:2023 continues to name missing
execution/resource limits as a resource-consumption risk.  The design response
here is not a new registry: batch accepted metadata work, cache it for one
palette build, and keep exact open/save/recovery paths on their existing live
bounded checks.

Research references:

- https://docs.python.org/3/library/subprocess.html
- https://discuss.python.org/t/graceful-exit-from-threadpoolexecutor-when-blocked-on-io-problem-and-possible-enhancement/80380
- https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/

## What changed

`src/micromax_editor/file_access.py` adds `stat_paths_contained_bounded()`, a
small batch wrapper around the existing fd-backed `stat_path_contained()` seam.
It deduplicates a bounded input set, runs the accepted metadata observations in
one killable filesystem worker when a positive timeout is configured, omits
per-path errors as best-effort palette truth, and still represents ordinary
missing files with `exists=False` results.

`src/micromax_editor/editor.py` adds a one-build `_palette_fs_stat_cache` plus
`_seed_palette_fs_stat_cache()`.  `command_palette_recent_file_rows()`,
`recent_inventory_rows()`, and known-path completion now preseed visible recent
and buffer paths through the batch stat seam before rendering row cues.  The
row builders then reuse the cache instead of falling back to a single timeout
worker for every visible row.  The cache is cleared at palette/recent inventory
entry points so it does not become a durable stale disk-state cache.

`tools/mxaudit.py` adds `palette_recent_stat_batch_boundary`, which hard-checks
the batch worker, palette cache, seeded recent rows, known-path preseed, and the
focused regression that refuses fallback to single-row stat during known-path
completion.

## Validation

Focused validation passed:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_command_palette_path_completion.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_editor_recent_register_authority.py tests/test_editor_buffer_lifecycle_recent.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mxaudit.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxaudit.py --check --limit 5
```

This is not a full release-suite claim.

## Remaining risk

The batch worker bounds a group of palette metadata observations, not every
possible path-shaped UI helper.  Exact single-path surfaces may still use the
single bounded stat seam when no batch preseed exists.

The larger filesystem-effect audit is still hand-checked by string predicates.
Once the current resource leaks are closed, the next refactor should generate
that audit slice from one effect table instead of adding another bespoke
predicate.

# Rev875 / rev0917 — status slow refresh

## Why this pass

Rev0916 stopped status rendering from probing disk every frame, but its cache
miss was still a synchronous metadata probe.  That left a bad shape for remote,
stalled, or unusual filesystems: a cursor blink after cache expiry could still
pay the full path-stat/read-only observation cost.

The online check kept this pass deliberately modest.  Python documents
subprocess timeouts as kill-and-wait cleanup, which is appropriate for accepted
read/list/write workers, but status rendering is too hot for a process per row
or per render.  PEP 471 also explains that `os.scandir()` reduces repeated stat
calls by caching directory-entry metadata, reinforcing the local lesson: reduce
probe frequency and reuse explicit witnesses before inventing more workers.
OWASP API4:2023 continues to identify missing execution/resource limits as a
resource-consumption risk.

Research references:

- https://docs.python.org/3/library/subprocess.html
- https://peps.python.org/pep-0471/
- https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/

## What changed

`src/micromax_editor/options_default.py` adds `diskstate.refreshms` with a
default of `1000`.  `diskstate.cachems` remains the short fresh-cache window;
`diskstate.refreshms` is the slower live-probe cadence for the status hot path.
When a cached witness is older than `diskstate.cachems` but younger than
`diskstate.refreshms`, `status_model()` reuses it and marks the result with
`disk_status_stale=1` instead of probing the filesystem immediately.

`src/micromax_editor/editor.py` refactors status disk/read-only caching into a
small shared helper that stores both fresh and refresh deadlines.  Open/save
witness refresh now seeds a fresh disk-state cache row from the already-captured
signature, so the first status render after open/save does not do a duplicate
stat just to rediscover `fresh` or `new`.

Explicit recovery surfaces remain exact.  `disk_state_rows()`, disk-state
hostcalls, save preflight, revert, diff, and direct witness refresh still pass
through the live bounded paths instead of accepting stale status rows.

`tools/mxaudit.py` extends `editor_disk_state_cache_boundary` so the cache check
now requires the slow-refresh option, `refresh_at` deadline, seeded witness
cache, and exported stale flag.

## Validation

Focused validation passed:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_editor_fs_open_save.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mxaudit.py tests/test_revision_index.py tests/test_docs_living_hygiene.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxlint.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxaudit.py --check --limit 5
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxcontext.py --check
```

This is not a full release-suite claim.

## Remaining risk

The status path is now stale/throttled rather than live-on-cache-miss, but it is
still not an asynchronous poller.  Once the slow refresh deadline arrives, the
next status render can still perform a bounded live metadata probe.

Recent/known-path palette truth probes are still the next wasteful filesystem
surface.  They should be batched or cached; the per-row timeout-worker idea
should stay retired.

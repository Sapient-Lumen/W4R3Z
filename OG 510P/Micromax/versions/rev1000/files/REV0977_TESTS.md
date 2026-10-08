# Revision 0977 tests

## Scope

This is a risk-targeted test record, not a claim that the entire repository suite
ran. It covers the measured browser-launch failure, blocking desktop-controller
discovery, successful-detach descriptor ownership, shared subprocess capture,
non-finite process/worker deadlines, adjacent filesystem/save/plugin/shell/
clipboard users, generated contracts, portability, install packaging, repository
hygiene, and archive publication.

## Focused process and worker union — 140 passed

Six clean working-tree commands passed **140/140** tests. Their pytest-reported
durations total **34.60 s**:

```text
12 passed in 4.95 s
  tests/test_editor_open_url_process.py

88 passed in 5.98 s
  tests/test_editor_host_process.py
  tests/test_editor_hostcall_boundary.py
  tests/test_worker_process.py

22 passed in 3.69 s
  tests/test_file_write_worker_lifecycle.py
  tests/test_plugin_package_fingerprint_budgets.py
  tests/test_plugin_package_snapshots.py

4 passed in 0.85 s
  tests/test_editor_shell_hostcall_budget.py

9 passed in 0.38 s
  tests/test_editor_clipboard_external_export.py
  tests/test_editor_clipboard_external_import.py

5 passed in 18.75 s
  tests/test_effect_contracts.py
```

This lane includes the actual `ed.open-url` timeout/process-tree/post-failure VM
journey, a blocking `xdg-settings` controller-discovery process, the successful
background-browser descriptor inspection, and a descendant that escapes into a
new POSIX session before timeout. The browser tests use exact-PID cleanup and
leave no matching sleeper process behind.

## Adjacent save/write lifecycle — 12 passed

`tests/test_atomic_write_plan.py` plus exact save freshness, mkparents, atomic
write timeout/cleanup, and direct-write node IDs passed **12/12** in **1.10 s**
after file-write teardown moved onto the shared worker owner. The six Python 3.13
warnings are the expected existing warning for explicit legacy `fork` test
contexts in a multithreaded test process; they are not a failure or a new
start-method claim.

## Packaging and bounded preflight

- A fresh `pip wheel --no-build-isolation` produced
  `micromax-0.0.8-py3-none-any.whl`; archive inspection found
  `micromax_editor/open_url_child.py`, `open_url_process.py`, and
  `host_process.py` present. Installing that wheel into a fresh target and
  calling the bounded opener through `/bin/true` succeeded, proving the helper
  path is not source-tree-only.
- `python tools/mxdoctor.py`: three bounded lanes passed **19/19**, **9/9**, and
  **3/3** tests.

## Structural and generated contracts — 68 passed

The revision index, living-doc hygiene, context, structural audit, and archive
publisher/verifier tests passed **68/68**: 1 revision-index case, 4 living-doc
cases, 7 context cases, 4 audit cases, and all 52 archive-tool cases. The
archive-tool file ran as thirteen exact four-node shards because the execution
wrapper terminated the combined invocation after 30 seconds; every collected
node was run and passed, with no failed assertion hidden by the sharding.

Additional exact-tree checks:

- `python tools/mxaudit.py --check`: passed; both the open-URL process boundary
  and finite-worker-deadline/shared-teardown flags are true.
- `python tools/mxeffects.py --check`: passed; 24 generated effect/resource rows,
  including `ed.open-url` with its live six-second/16 KiB budgets.
- `python tools/mxportable.py --quiet`: **172/172** portability cases passed.
- `bash scripts/lint.sh`: `mxlint: ok`.
- `bash scripts/typecheck.sh`: mypy was not installed in the offline execution
  environment, so the script explicitly skipped type checking.

The context and structural checks are rerun after this record is written. Exact
archive verification remains external evidence and is not self-attested by the
ZIP it verifies.

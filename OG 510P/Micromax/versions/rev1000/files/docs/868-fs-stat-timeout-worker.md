# Rev0910 filesystem stat timeout worker

Rev0910 closes the first filesystem wall-clock seam left after the byte/row and
process-output budget passes: `ed.fs-stat`.  The stat hostcall was already
capability-gated and fd-bound for containment, but its accepted metadata path
still ran in the editor process.  On unusual, remote, or stuck filesystems, the
open/fstat path can hang after capability preflight and before the VM has any
stack/result budget to inspect.

## Why this cut

Online research kept the landing narrow:

- OWASP API4:2023 treats execution time, memory, process count, payload size,
  operation count, and returned records as resource controls.  Micromax has now
  covered many payload and row surfaces; metadata wall time was the next missing
  control on a script-visible hostcall.
  Source: https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- Python's `subprocess` docs make timeout behavior explicit for child processes:
  timeout is a process-boundary property, not something generic file APIs expose
  at the call site.  That supports using a killable worker for blocking host
  operations rather than pretending `os.open`/`os.fstat` has a portable timeout
  knob.  Source: https://docs.python.org/3/library/subprocess.html
- Python's `multiprocessing` docs expose process `terminate()`/`kill()` controls
  that do not exist for an arbitrary in-process Python thread blocked inside a
  host operation.  That is the right primitive for a cooperative editor host
  that needs to recover from a bounded observation.  Source:
  https://docs.python.org/3/library/multiprocessing.html

## Landing

- `src/micromax_editor/file_access.py` adds
  `FilesystemOperationTimeoutError` and `stat_path_contained_bounded()`.  The
  existing `stat_path_contained()` remains the fd-bound containment oracle; the
  new wrapper runs it in a short-lived worker when the timeout is positive and
  terminates/kills the worker on expiry.
- `src/micromax_editor/hostcall_boundary.py` adds
  `DEFAULT_FS_STAT_TIMEOUT_SECONDS` and `effective_fs_stat_timeout_seconds()` as
  a VM-tunable hostcall boundary.  Non-positive values intentionally disable the
  worker for embedders with stronger filesystem containment.
- `src/micromax_editor/fs_hostcalls.py` routes `ed.fs-stat` through the bounded
  stat wrapper while preserving the previous `{ok info err}` tuple shape.
- `src/micromax_editor/micromax_bridge.py` installs
  `editor_hostcall_fs_stat_timeout_seconds` on the VM and passes it to
  `fs_stat_path()`.
- `tools/mxaudit.py` now hard-checks `fs_stat_timeout_worker`, so the filesystem
  wall-clock seam cannot be reported as handled while the bridge silently falls
  back to unbounded stat.

## Guarantees

- `ed.fs-stat` remains capability-gated by `cap.fs-stat`.
- `cap.fs-root` checks still happen before the worker, and the worker still uses
  the fd-bound target containment check before returning metadata.
- A timed-out stat returns the normal hostcall tuple with `ok=0`, an empty info
  map, and a diagnostic error string instead of freezing the editor process.
- The timeout is VM-tunable through `editor_hostcall_fs_stat_timeout_seconds` and
  can be disabled by setting it to a non-positive value.

## Risks left

- This is only the first filesystem wall-clock boundary.  `ed.fs-read`,
  `ed.fs-list`, command-driven open/save, and prompt completion still have
  accepted filesystem work that can stall after preflight.
- The worker is still an in-process Python reference-host technique, not an OS
  sandbox for hostile plugins or hostile filesystems.
- Fork-based worker startup is used where available to keep the reference host
  small and testable.  Embedders with multithreaded or hostile-code constraints
  should prefer an external process/container boundary for filesystem effects.

## Validation

Focused validation run during the rev0910 landing:

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_fs_stat.py tests/test_editor_fs_read.py tests/test_editor_fs_list.py tests/test_mxaudit.py
```

Additional validation before the package:

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_fs_stat.py tests/test_editor_fs_read.py tests/test_editor_fs_list.py tests/test_mxaudit.py tests/test_mxcontext.py tests/test_revision_index.py
python tools/mxaudit.py --check
python tools/mxcontext.py --check
python tools/mxlint.py
python tools/mxportable.py --quiet
```

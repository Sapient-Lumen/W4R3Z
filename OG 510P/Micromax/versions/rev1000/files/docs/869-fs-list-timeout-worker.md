# Rev0911 filesystem list timeout worker

Rev0911 extends the filesystem wall-clock boundary from metadata observation to
script-visible directory listing.  `ed.fs-list` was already capability-gated,
root-contained, and row-budgeted, but accepted directory work still ran in the
editor process.  A slow remote directory, a wedged mount, or child-kind metadata
lookups could therefore stall after capability/root preflight and before the VM's
post-hostcall result budget could inspect returned rows.

## Why this cut

Online research kept the landing concrete rather than doctrinal:

- OWASP API4:2023 names execution timeouts, memory, process count, payload size,
  operation count, and number of records as resource controls.  Rev0911 applies
  the same principle to `ed.fs-list`: row budgets cap records, while a worker
  timeout caps accepted directory traversal wall time.  Source:
  https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- PEP 471 describes `os.scandir()` as an iterator rather than an eager list,
  which is useful for Micromax's row budget, but it is still filesystem work in
  the caller's process.  A separate killable worker is the recovery boundary for
  blocking directory traversal.  Source: https://peps.python.org/pep-0471/
- CWE-400 frames uncontrolled resource consumption as a failure to limit how many
  finite resources an actor can cause the system to spend.  Directory traversal
  combines time, metadata calls, file descriptors, and row production, so it
  belongs in the same resource-budget family as shell output, clipboard helpers,
  regex workers, and `ed.fs-stat`.  Source:
  https://cwe.mitre.org/data/definitions/400.html

## Landing

- `src/micromax_editor/file_access.py` adds `list_dir_contained_bounded()`.  The
  existing `list_dir_contained()` remains the fd-bound containment and row-budget
  oracle; the new wrapper runs it in a short-lived worker when the timeout is
  positive and terminates/kills the worker on expiry.
- `src/micromax_editor/hostcall_boundary.py` adds
  `DEFAULT_FS_LIST_TIMEOUT_SECONDS` and `effective_fs_list_timeout_seconds()` as
  the VM-tunable wall-clock sibling of `effective_fs_list_max_rows()`.
- `src/micromax_editor/fs_hostcalls.py` routes `ed.fs-list` through the bounded
  wrapper and returns the normal `{ok rows err}` shape on timeout.
- `src/micromax_editor/micromax_bridge.py` installs
  `editor_hostcall_fs_list_timeout_seconds` on the VM and passes the effective
  timeout to the hostcall helper.
- `tools/mxaudit.py` now hard-checks `fs_list_timeout_worker`, so the directory
  listing wall-clock seam cannot silently regress while scan/row budgets still
  look green.

## Guarantees

- `ed.fs-list` remains capability-gated by `cap.fs-list`.
- `cap.fs-root` preflight still happens before the worker, and the worker still
  opens the directory and verifies the fd target before scanning entries.
- Positive row limits still stop entry collection before materializing an
  unbounded name list; the timeout is a sibling wall-clock boundary, not a
  replacement for the row budget.
- A timed-out listing returns the normal hostcall tuple with `ok=0`, empty rows,
  and a diagnostic error string instead of freezing the editor process.
- The timeout is VM-tunable through `editor_hostcall_fs_list_timeout_seconds` and
  can be disabled by setting it to a non-positive value.

## Risks left

- `ed.fs-read`, command-driven open/save, and prompt-completion filesystem paths
  still have accepted filesystem work that can stall after preflight.
- The worker is a reference-host recovery boundary, not a hostile-code or
  hostile-filesystem sandbox.
- Fork-backed tests keep the reference host small, but embedders with strict
  multithreaded or hostile-code requirements should replace the reference worker
  with a stronger external filesystem-effect boundary.

## Validation

Focused validation run during the rev0911 landing:

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_fs_list.py tests/test_editor_fs_stat.py tests/test_mxaudit.py
```

Additional validation before the package:

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_fs_list.py tests/test_editor_fs_stat.py tests/test_mxaudit.py tests/test_mxcontext.py tests/test_revision_index.py
python tools/mxaudit.py --check
python tools/mxcontext.py --check
python tools/mxlint.py
python tools/mxportable.py --quiet
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python tools/mxtimely.py --skip-tests --skip-doctor --summary-json .artifacts/mxtimely-summary.json
```

# Rev0914: atomic write timeout boundary

## Why this was next

Rev0913 moved command open/revert/source/user-init reads and prompt path completion onto bounded filesystem seams.  The riskiest remaining filesystem lane was the write side: once a save had passed capability, containment, and freshness checks, the final open/write/fsync/rename sequence could still block on an unusual filesystem.  That is worse than a slow prompt list because it sits on a data-loss boundary and may already have created a temporary file.

The current online read reinforced the shape of the fix rather than a new doctrine pass:

- OWASP API4:2023 names missing execution timeouts, file-descriptor/process ceilings, and related resource limits as unrestricted resource-consumption risks.
- Python's subprocess documentation treats process timeout as a kill/wait boundary for `subprocess.run`, and its lower-level `Popen.communicate()` guidance says callers must kill the child and finish cleanup after timeout.
- Python's `ThreadPoolExecutor` documentation warns that all queued threads are joined before interpreter exit and recommends not using it for long-running tasks; thread workers are therefore the wrong abstraction for filesystem work that may block indefinitely.
- WIT/WASI remains a useful later model for declaring imports/exports and host resources, but this pass needed one executable save boundary, not another registry.

## What changed

`src/micromax_editor/file_write.py` now keeps the old writer implementation as `_write_file_bytes_impl()` and exposes `write_file_bytes(..., timeout_seconds=...)` as the public wrapper.

When `timeout_seconds` is positive and `atomic=True`, the wrapper runs the existing atomic writer in a short-lived worker process.  The worker still uses the same implementation, so the following behavior is preserved:

- symlink-target saving rather than replacing the visible symlink;
- `cap.fs-root` containment checks;
- dirfd parent binding where the host supports it;
- external freshness checks and optional digest witnesses;
- permission preservation;
- atomic temp-file replacement;
- optional file and directory fsync;
- the existing `FileWriteResult` shape.

If the worker exceeds the wall-clock budget, the parent terminates it, tries a stronger kill if needed, and raises `FileWriteTimeoutError` with a normal save failure message.  The parent also performs best-effort cleanup of temp files whose names match the killed worker pid and the target basename.  Cleanup uses the existing dirfd-bound parent path when available so recovery does not silently follow a swapped parent pathname.

`src/micromax_editor/hostcall_boundary.py` adds `DEFAULT_FILE_WRITE_TIMEOUT_SECONDS` and `effective_file_write_timeout_seconds()`.  `src/micromax_editor/micromax_bridge.py` installs `editor_file_write_timeout_seconds` on editor VMs.  `src/micromax_editor/editor.py` passes the effective timeout into ordinary saves, and `src/micromax_editor/persist_io.py` passes the same timeout into small editor-owned persistence writes.

`tools/mxaudit.py` now hard-checks `editor_atomic_write_timeout_boundary` so future revisions cannot silently drop the worker, VM setting, editor/persistence callsites, or temp cleanup seam.

## Deliberate non-change: direct writes

`save.atomic=false` remains in-process even if a timeout is configured.  Killing a direct writer can leave the real target truncated or partially rewritten.  That would turn a liveness fix into a data-loss bug.  Direct writes still use the existing fd-bound direct writer and freshness checks, but they do not get process-kill timeout semantics until a future design can provide resumable or journaled recovery for the real target.

## Tests and evidence

Focused validation for the landing:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q \
  tests/test_editor_fs_open_save.py::test_atomic_file_writer_timeout_kills_worker_and_cleans_temp \
  tests/test_editor_fs_open_save.py::test_direct_file_writer_timeout_stays_in_process_to_avoid_partial_kill \
  tests/test_editor_fs_open_save.py::test_save_atomic_option_can_use_legacy_direct_write_path \
  tests/test_editor_fs_open_save.py::test_save_passes_vm_tunable_atomic_write_timeout \
  --durations=10
```

Result: 4 passed.

Broader focused validation for this pass:

```bash
python -m py_compile \
  src/micromax_editor/file_write.py \
  src/micromax_editor/editor.py \
  src/micromax_editor/hostcall_boundary.py \
  src/micromax_editor/micromax_bridge.py \
  src/micromax_editor/persist_io.py \
  tools/mxaudit.py \
  tests/test_editor_fs_open_save.py
```

Result: passed.

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPYCACHEPREFIX=/tmp/micromax_pycache \
  python -m pytest -q tests/test_editor_fs_open_save.py --durations=10
```

Result: 72 passed.

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPYCACHEPREFIX=/tmp/micromax_pycache \
  python -m pytest -q \
  tests/test_editor_script_context_fs_caps.py \
  tests/test_editor_persistence_cap_persist.py \
  tests/test_mxaudit.py \
  tests/test_mxcontext.py \
  tests/test_revision_index.py \
  --durations=20
```

Result: 94 passed.

```bash
PYTHONPYCACHEPREFIX=/tmp/micromax_pycache python tools/mxaudit.py --check
PYTHONPYCACHEPREFIX=/tmp/micromax_pycache python tools/mxcontext.py --json --check >/tmp/micromax-rev0914-context.json
```

Result: both passed; `mxaudit` reports `atomic-write-timeout=True`, and `mxcontext` reports rev0914 with clean context and revision-source checks.

A single combined pytest lane over the same selected files hit the outer cloudtainer timeout after printing completion dots, so the evidence claim for rev0914 is intentionally split-lane, not a full release-suite claim.

## Remaining risk

The save path still has pre-commit filesystem work outside this new worker: directory checks, freshness capture, optional digest reads, parent creation, and some status/disk-state probes.  Those are now the highest-leverage save-side risks.  The next pass should avoid wrapping everything in one huge worker blindly; the better shape is to move preflight stat/hash/parent creation onto explicit bounded seams so cleanup ownership stays obvious.

The filesystem-resource audit is also too hand-coded.  The right next registry work is not a broad doctrine document; it is a small generated table for the live filesystem effects that already have code: stat, list, read, open/revert/source/user-init reads, prompt completion, and atomic write.

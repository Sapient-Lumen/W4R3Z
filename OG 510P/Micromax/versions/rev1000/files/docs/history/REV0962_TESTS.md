# Revision 0962 validation

Rev0962 was accepted with bounded slices around the changed save, recovery,
permission, synchronization, subprocess, and worker-lifecycle seams. Counts
below overlap and must not be summed into a synthetic total. No complete
full-suite claim is made.

## Process-death matrix

- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_save_crash_matrix.py --basetemp=/mnt/data/mx-r962-crash-overlay`: **13 passed** on Linux overlayfs.
- The same matrix with `--basetemp=/dev/shm/mx-r962-crash-tmpfs-2`: **13 passed** on Linux tmpfs.

The matrix includes checkpoint temp/replace/directory-sync, document temp,
replace, mode restoration, metadata sync, directory sync, journal unlink, and
direct-write truncate/file-sync process deaths.

## Focused regression slices

- Complete interrupted-save and recovery-journal journey files: **44 passed**.
- New sync-witness, private-temp, permission restoration, error propagation, and
  cleanup slice: **42 passed, 81 deselected**.
- Atomic/direct writer, symlink, freshness, permission, missing-target race, and
  timeout slice: **27 passed, 63 deselected**.
- Bounded freshness/mkparents/write timeout and VM option-plumbing slice: **5
  passed**.
- File-worker result ordering, incomplete-result feeder cancellation, join-failure,
  non-exiting-child, liveness-failure, and start-failure cleanup: **6 passed**.
- Worker-context/native-thread regressions: **7 passed**.
- Test-supervisor regressions: `mxtest` **123 passed**; `mxdoctor` **21 passed**.
- Uploaded-lineage plugin/screen compatibility slice: **48 passed**.

## Repository acceptance

- `mxcontext --check`: passed at rev0962.
- `mxaudit --check`: passed; 23-row generated effect/resource contract current.
- `mxeffects --check` and `mxlint`: passed.
- Portability suite: **156 passed, 0 failed**.
- Revision index, living docs, Makefile handoff, context, audit, installed-resource,
  effect-contract, and archive-tool regressions: **60 passed**.
- `test_editor_fs_open_save.py`: all **90** collected nodes passed in bounded
  slices; `test_editor_interrupted_save_recovery.py`: all **12** nodes passed.
- `mypy` was not installed in this offline cloudtainer, so the repository's
  typecheck script reported its documented skip rather than a passing typecheck.
- Archive provenance verification is rerun on the emitted zip after creation.

## Honest limits

The first broad mixed save invocation exceeded its 120-second outer command
window after five tests. It left no matching worker process, and no result from
that attempt is claimed. Subsequent bounded slices completed cleanly. The tests
simulate process death, not power interruption or storage-controller failure.

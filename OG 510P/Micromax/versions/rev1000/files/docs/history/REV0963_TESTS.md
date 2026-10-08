# Revision 0963 validation

Rev0963 was accepted with isolated slices around atomic planning, permission
repair, process identity, stale-temp inventory/cleanup, process-death restart,
audit integrity, and archive lineage. Counts overlap and are not summed. No
complete full-suite claim is made.

## New focused contracts

- `tests/test_atomic_write_plan.py`, `tests/test_recovery_mode_repair.py`,
  `tests/test_save_residue.py`, and `tests/test_recovery_temp_residue.py`:
  **39 passed**.
- Coverage includes parent and symlink drift, exact final-mode propagation,
  unnamed-probe preference and error classification, named-probe unlink timing,
  resumable post-`chmod` death, intended `0600`, unavailable directory sync,
  hard-link/symlink/parent replacement refusal, pre-`fchmod` mode races,
  v2/v3 identity behavior, cross-namespace unknown state, exact PID+lease
  timeout cleanup, one-scan parent deduplication, bounded inventory, and
  descriptor-relative stale cleanup.

## Restart and integration regressions

- `tests/test_save_crash_matrix.py`: **15 passed** in the final process-death run.
- `tests/test_editor_interrupted_save_recovery.py`: **14 passed** in its completed
  verbose run.
- `tests/test_recovery_journal_journey.py`: **35 passed**.
- `tests/test_file_write_worker_lifecycle.py`: **6 passed**.
- Selected atomic writer privacy, timeout cleanup, replace-fault cleanup,
  descriptor lifecycle, new-file mode restoration, and real directory-fsync
  failure cases in `tests/test_editor_fs_open_save.py`: **7 passed**.

## Audit, docs, and packaging regressions

- `tests/test_mxaudit.py`: **4 passed**, including local-alias timeout-flow
  detection and docstring line-wrapping regressions.
- `tests/test_effect_contracts.py`: **5 passed**; generated `ed.save` audit rows
  report both timeout boundaries as present.
- Revision-index, living-doc, and context tests: **11 passed**.
- `tests/test_mkrevzip.py`: **34 passed** with one expected duplicate-member
  warning in its rejection test.
- Portability suite: **156 passed, 0 failed**.

## Repository and archive acceptance

- `python -m compileall -q src tests tools`: passed.
- `python tools/mxlint.py`: passed.
- `python tools/mxaudit.py --check`: passed, including a current generated
  effect/resource contract.
- `python tools/mxeffects.py --check-help-doc --check`: passed.
- `PYTHONPATH=tools:src python tools/mxcontext.py --check`: passed.
- The emitted rev0963 archive was checked by `mkrevzip --verify-archive`, which
  validates canonical naming, revision agreement, member safety, embedded
  context, and provenance hashes.

## Runtime observations and honest limits

- The current process identity classified active in the actual cloudtainer.
- Real workspace probing reported `O_TMPFILE` unavailable, exercising the named
  empty-probe fallback; the unnamed path is unit-tested with deterministic fd
  witnesses.
- Two combined sequential invocations exceeded their outer command budgets after
  making partial progress but before a pytest summary. Their dots are not counted
  as evidence. The relevant suites were rerun separately and passed as listed
  above.
- Focused and packaging checks do not establish a complete repository suite,
  sudden-power-loss durability, remote-filesystem behavior, or Windows behavior.

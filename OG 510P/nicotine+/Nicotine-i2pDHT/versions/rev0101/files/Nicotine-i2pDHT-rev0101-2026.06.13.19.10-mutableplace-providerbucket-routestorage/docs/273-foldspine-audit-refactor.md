# Foldspine audit/refactor

The cube accumulated many revision-specific fold modules. `foldspine.py` starts a smaller declarative current-revision spine. It checks modules, tests, docs, public-surface pointers, head-registry pointers, docs index text, README/START_HERE revision visibility, and the active surface ledger.

Historical fold modules remain for regression and wake-from-amnesia. The refactor is additive, not a history deletion.

## Compile-check refactor

The rev0028 audit lane also fixes the compile hygiene check for Python 3.13-era behavior: active Python surfaces are now compiled into temporary `.pyc` targets instead of trying to use `/dev/null` as a bytecode sink. This keeps the no-persistent-bytecode property while avoiding a non-regular-file trap in `py_compile`.
## Duplicate active-test fold

A duplicate active rev0028 test file was moved to `artifacts/branchlets/rev0028_duplicate_active_tests/` after the canonical active test was pinned as `tests/test_rev0028_journal_generator_refusal_sam_fold.py`. This keeps the behavioral evidence while reducing current-test surface ambiguity.

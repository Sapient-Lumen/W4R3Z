# Validation-harness isolation correction — rev0073

## Failure observed during construction

A draft U-123 disposition probe extracted unpatched, selected, and strict states beneath one temporary parent. After focused test execution, the strict state could no longer import `pynicotine`, and both later upstream-unit lanes reported that their source test paths did not exist. Those were gate failures caused by missing temporary source trees, not product test failures.

The precise cleanup actor was not established. Rather than normalizing or retrying the results, rev0073 changed the architecture so sibling validity cannot depend on a shared temporary parent.

## Corrective design

```text
independent source roots:
  one mkdtemp root per unpatched/selected/strict state

independent runtime roots:
  separate HOME, XDG_CONFIG_HOME, XDG_DATA_HOME, XDG_CACHE_HOME, TMPDIR, and CWD

ordering:
  upstream parity before focused disposable harnesses

parallelism:
  baseline and selected unit suites run concurrently, never in one process

process control:
  child process groups receive hard timeout cleanup

acceptance:
  no parsed zero-test result can satisfy an expected failure
```

## Final observation

The corrected run produced:

```text
classified test expectations: 18/18
burst-state expectations: 3/3
unpatched upstream units: 58 passed, 1 skipped
selected upstream units: 58 passed, 1 skipped
outcome parity: pass
native combined-patch suite: 60 passed, 1 skipped
```

The correction is encoded in `tools/probe_rev0073_u123_disposition.py`; runtime records are under `evidence/rev0073-u123-runtime/`.

## Namespace correction

A pre-disposition construction probe wrote a different result schema to the canonical `rev0073_u123_test_matrix.*` paths. It is archived under `tools/archive/rev0073/`. The replacement `tools/probe_rev0073_u123_native_patch.py` writes only `rev0073_u123_native_patch_*`, so the disposition and native-patch gates cannot clobber each other.

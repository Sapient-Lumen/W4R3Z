# Rev847 — source-dependency workflow/config sensitivity

Rev847 audits the chunk source-dependency heuristic after the aggregate lane became reliable enough to trust. The risky gap was not another runtime seam; it was the opposite: some non-runtime files were already partitioned in the source manifest but were not requested by chunk dependency detection.

Two cases are now explicit:

- tests that inspect `Makefile` / handoff workflow depend on the `workflow` partition;
- tests that inspect packaging/test configuration such as `pyproject.toml`, installed resource declarations, or the installed-help manifest depend on the `test-config` partition.

This keeps resume behavior honest. A README-only handoff edit should not rerun plain VM/editor tests, but a Makefile edit must invalidate the Makefile handoff tests, and a pyproject/package-data edit must invalidate installed-resource/package tests.

The implementation stays heuristic and conservative. It does not attempt dynamic tracing; it extends the existing selected-test-file token scan with workflow/config tokens and regression coverage in `tests/test_mxtest.py`.

## Interrupt preservation audit

While rebuilding the current-source manifest, an outer SIGTERM landed during a portability-heavy per-test batch. The existing budget-stop logic preserved later already-passed chunks for `max-new-*` and `max-runtime-seconds` stops, but interruption stops still replaced later matching evidence with `not_run` records.

Rev847 fixes that too: `interrupted-*` stop reasons now preserve later chunks whose source dependency, environment, and chunk identity still match. This prevents a cloudtainer-level interrupt from erasing known-good tail evidence in the archive-carried manifest.

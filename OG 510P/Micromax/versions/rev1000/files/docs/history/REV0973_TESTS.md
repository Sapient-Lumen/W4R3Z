# Revision 0973 test evidence

## Scope

This revision changes VM budget semantics and every plugin execution turn. The
evidence is split into focused process-sized lanes because several historical
plugin/worker suites are intentionally process-heavy. No complete repository
suite or hostile-code sandbox claim is made.

## Focused liveness regressions

`PYTHONPATH=src pytest -q tests/test_plugin_execution_budget.py`

- **13 passed**.
- Covers unbypassable `VM.eval` fuel; nested host composition; exact integer
  validation; `set-budget`/`with-budget` separation; source/init/deinit loops;
  command/key/timer/hook loops; safe tuning; script-state restoration; rollback;
  force-unload recovery; and post-failure VM usability.

## Plugin authority and compatibility

`PYTHONPATH=src pytest -q tests/test_plugin_surface_contract.py tests/test_plugin_reload_recovery.py tests/test_plugin_runtime_group_policy.py tests/test_plugin_runtime_group_reports.py tests/test_restricted_plugin_journey.py tests/test_plugin_callback_scoped_snapshot.py`

- **118 passed**.
- Retains declared imports, dictionary ownership, internal-model denial,
  generation/reload, runtime-group, restricted-workspace, and callback rollback
  behavior around the new execution context.

`PYTHONPATH=src pytest -q tests/test_features.py tests/test_smoke.py tests/test_editor_timer_authority.py tests/test_editor_hook_authority.py tests/test_editor_highlight_and_timers.py`

- **46 passed**.
- Retains core language behavior, standalone smoke, timer/hook authority, and
  editor timer/highlight integration.

Focused containment callbacks were also rerun in smaller process groups:

- first 15 cases of `test_plugin_containment_and_caps.py`: **15 passed**;
- namespace/include/rollback/stack-isolation callback slice: **8 passed**.

A larger combined process-heavy invocation was stopped by its outer command
limit after partial progress; those partial dots are not counted as a passing
lane.

## Language portability

`PYTHONPATH=src python tools/mxportable.py --quiet`

- **157/157 portability cases passed**.
- The new case proves clearing the persistent base cannot erase an active
  `with-budget` frame. Host-owned embedding fuel intentionally remains outside
  the portable language surface.

## Generated contracts, structural checks, and packaging

The final source tree passed:

- `python -m compileall -q src tests tools`;
- `python tools/mxlint.py` — **ok**;
- `python tools/mxeffects.py --write-help-doc --check-help-doc --check` —
  **23 live effect/resource rows**, generated help current at rev0973;
- `python tools/mxaudit.py --check` — **no audit-integrity errors**;
- `python tools/mxcontext.py --json --check` — **64 curated documents**, 55
  code entrypoints, no missing paths or revision warnings;
- `python tools/mxrelease.py --package-inputs --package-inputs-json` — package
  inputs **ok**, with the declared `unlocked-dev-only` dependency policy.

Focused release-seam tests passed:

- `tests/test_editor_require_caps.py` — **19 passed**;
- revision index, generated context, living-doc hygiene, structural audit, and
  effect-contract files — **21 passed** total; the five effect-contract nodes
  were run separately after unrelated abandoned worker jobs contended for the
  process machinery;
- ten selected `test_mkrevzip.py` integration/verifier cases — **10 passed**,
  covering current-context reuse, revision mismatch, embedded context,
  deterministic double construction, generated-archive verification, verifier
  CLI JSON, repository breadcrumb disagreement, `--rev` assertion behavior,
  archived-source mismatch, and normalized snapshot modes.

`bash scripts/typecheck.sh` reported that mypy is not installed in the offline
container and skipped. This is recorded as an unavailable lane, not a pass.

The linked ZIP is produced only after cache cleanup, final context regeneration,
`tools/mkrevzip.py --verify-archive`, ZIP CRC verification, lineage verification,
and filename-policy verification complete. No complete repository-suite result
is claimed.

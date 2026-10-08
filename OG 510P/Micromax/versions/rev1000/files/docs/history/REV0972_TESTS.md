# Revision 0972 test evidence

This file records scoped evidence from the final source generation. It is not a complete repository-suite claim.

## Executable plugin surface and rollback

```bash
PYTHONPATH=src pytest -q \
  tests/test_plugin_surface_contract.py \
  tests/test_plugin_reload_recovery.py
```

Result: **34 passed in 18.13s**.

This covers explicit context validation, undeclared sibling rejection, declared dependency read-only behavior, `is`/`defer!` ownership, module creation denial, exact source/lifecycle/delayed-callback order, direct-before-transitive precedence, raw `set-current`, final `_add_word` enforcement, transitive late binding, filtered hook inventory, internal model probes/calls, trusted model access, stack preservation, classification bounds, bundled-hostcall classification, and reload rollback.

## Standalone VM compatibility

```bash
PYTHONPATH=src pytest -q tests/test_features.py tests/test_smoke.py --durations=10
```

Result: **26 passed in 0.26s**.

This includes ordinary wordlist/search-order isolation outside an embedding scope, core language behavior, package loading, hooks, host bridge behavior, and smoke journeys.

## Portability corpus

The 36-case portability file was split only to keep each process under the execution window:

```bash
mapfile -t nodes < <(PYTHONPATH=src pytest --collect-only -q \
  tests/test_portability_suite.py | grep '::')
PYTHONPATH=src pytest -q "${nodes[@]:0:27}" --durations=8
PYTHONPATH=src pytest -q "${nodes[@]:27:9}" --durations=8
```

Results: **27 passed in 21.28s** and **9 passed in 21.73s**.

## Plugin authority and lifecycle matrix

```bash
PYTHONPATH=src pytest -q \
  tests/test_plugin_reload_recovery.py \
  tests/test_plugin_runtime_group_policy.py \
  tests/test_plugin_runtime_group_reports.py \
  tests/test_restricted_plugin_journey.py \
  tests/test_plugin_callback_scoped_snapshot.py
```

Result: **101 passed in 20.43s**.

```bash
# The 56-case containment/capability file was run in four collected-node slices.
PYTHONPATH=src pytest -q <collected nodes 0:14 from tests/test_plugin_containment_and_caps.py>
PYTHONPATH=src pytest -q <collected nodes 14:28 from tests/test_plugin_containment_and_caps.py>
PYTHONPATH=src pytest -q <collected nodes 28:42 from tests/test_plugin_containment_and_caps.py>
PYTHONPATH=src pytest -q <collected nodes 42:56 from tests/test_plugin_containment_and_caps.py>
```

Results: **14 passed in 12.79s**, **14 passed in 16.23s**, **14 passed in 10.93s**, and **14 passed in 10.36s**.

```bash
PYTHONPATH=src pytest -q \
  tests/test_plugin_hostcalls.py \
  tests/test_plugin_json_schema.py \
  tests/test_plugin_load_errors.py \
  tests/test_plugin_package_fingerprint_budgets.py \
  tests/test_plugin_package_snapshots.py \
  tests/test_plugin_retired_wordlists.py
```

Result: **34 passed in 14.37s**.

## Editor authority and hostcall boundary

```bash
# The live 99-case collection was executed in bounded collected-node slices
# because process-heavy grant cases exceed the shell window when combined.
PYTHONPATH=src pytest --collect-only -q \
  tests/test_editor_plugin_authority.py \
  tests/test_editor_plugin_clipboard_cleanup.py \
  tests/test_editor_plugin_file_navigation_cleanup.py \
  tests/test_editor_plugin_help_history_cleanup.py \
  tests/test_editor_plugin_manual_load_grants.py \
  tests/test_editor_plugin_option_rollback.py \
  tests/test_editor_plugin_palette_recent_cleanup.py \
  tests/test_editor_pluginpick.py \
  tests/test_editor_hook_authority.py
```

Result: **99 passed across bounded slices**.

```bash
PYTHONPATH=src pytest -q \
  tests/test_editor_hostcall_boundary.py \
  tests/test_editor_hostcall_registry.py \
  tests/test_editor_hostcall_state_argument_boundary.py \
  tests/test_editor_hostcall_transactions.py \
  tests/test_hostcall_result_budget.py
```

Results: **56 passed in 3.01s** and **26 passed in 0.90s** (82 total).

## Specialized line geometry and editor continuation

```bash
PYTHONPATH=src pytest -q \
  tests/test_line_edit_geometry.py \
  tests/test_multicursor_edit_journey.py \
  tests/test_editor_core.py \
  tests/test_editor_clipboard_authority.py \
  tests/test_editor_selection_stack_authority.py \
  tests/test_editor_undo_authority.py \
  tests/test_editor_with_undo_transaction.py \
  tests/test_visible_selection_projection.py
```

Result: **132 passed in 9.55s**.

The focused pure/application file has 14 tests, including exhaustive valid move spans and directions over a six-line source, fully/partially selected cut spans, and half-open whole-line cut boundaries. Combined plugin-surface, reload-recovery, and line-geometry evidence is **48 passed in 16.55s**. The fresh-process rev0971/final-rev0972 4,000-line/1,000-cursor cut-line probe measured medians of **0.642s** and **0.050s** with 1,000 versus one version increments; it is scoped performance evidence, not a test guarantee.

## Release/document checks

The final source generation passes Python compilation, `tools/mxlint.py`, `tools/mxeffects.py --check`, `tools/mxaudit.py --check`, and `tools/mxcontext.py --check`. The repository typecheck wrapper ran but reported an explicit offline skip because `mypy` is not installed in the environment.

The combined context, revision-index, living-document, and archive-tool lane passes **64 tests**. The curated context contains exactly **64 documents**, reports revision 972 with no missing paths or revision warnings, and excludes archived history from the hot handoff while retaining it in the package. Exact archive provenance and member digests are checked after packaging; this remains scoped evidence rather than a complete repository-suite claim.

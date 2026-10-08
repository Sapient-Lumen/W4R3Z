# Revision 0975 tests

## Search, replacement, and worker journey lane

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
pytest -q \
  tests/test_regex_containment.py \
  tests/test_regex_hostcalls.py \
  tests/test_effect_contracts.py \
  tests/test_replace_plan.py \
  tests/test_editor_query_replace.py \
  tests/test_editor_qreplace_interaction_boundary.py \
  tests/test_qreplace_generation_journey.py \
  tests/test_query_replace_buffer_witness.py \
  tests/test_search_navigation_journey.py \
  tests/test_editor_search_authority.py \
  tests/test_tui_hlsearch.py
```

Result: **136 passed**.

This lane includes Linux default-headroom native-repeat pressure, a tuned smaller
ceiling, stable `memory-limit` classification, immediate fresh-worker recovery,
pure-executor `RLIMIT_AS` non-mutation, the prebuilt final-response fallback,
exact surrogate UTF-8 accounting, denial before source slicing, hostcall stack
preservation, editor search navigation/projection, and immutable query-replace
journeys.

## Compatibility and adjacent resource regressions

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
pytest -q \
  tests/test_features.py tests/test_smoke.py tests/test_core_registry.py \
  tests/test_vm_callstack.py tests/test_plugin_surface_contract.py \
  tests/test_plugin_reload_recovery.py \
  tests/test_string_preallocation_budget.py tests/test_value_text_budget.py \
  tests/test_string_hostcalls.py tests/test_hostcall_result_budget.py \
  tests/test_plugin_execution_budget.py \
  tests/test_type_predicates_and_conversions.py
```

Result: **123 passed**.

## Structural, generated, and release evidence

- `python -m compileall -q src tests tools` — passed.
- `make lint` — `mxlint: ok`; Ruff was not installed in this offline image.
- `make typecheck` — explicitly skipped because mypy was not installed.
- `PYTHONPATH=src python tools/mxportable.py --quiet` — **157/157** cases passed.
- docs living-hygiene, docs-index, and generated effect-contract tests — **24 passed**.
- `tests/test_mxaudit.py` — **4 passed**; direct `tools/mxaudit.py --check` also passed.
- installed-runtime-resource tests — **2 passed**.
- Makefile handoff-manifest tests — **6 passed**.
- `tests/test_revision_index.py` — passed.
- `tests/test_mxcontext.py` — **7 passed** after the final package checklist and
  64-document context were regenerated.
- `tests/test_mxrelease.py` — **17 passed**.
- `tests/test_mkrevzip.py` — **52 passed**; the deliberate duplicate-member
  rejection case emits one `zipfile` warning.
- `make timely` — context, audit, lint, **157/157** portability, and doctor all
  passed.
- `tools/mxcontext.py --json --check` — rev0975, 64 documents, 56 code paths,
  no missing paths.
- package/dependency input policy inspection — passed.

## Scope of claim

These are focused product journeys, adjacent compatibility/resource tests,
structural/generated checks, and exact archive-generator/verifier tests. They do
not claim a complete repository suite, cross-platform memory enforcement, total
heap or RSS containment, syscall/crash isolation, or hostile-code sandboxing.

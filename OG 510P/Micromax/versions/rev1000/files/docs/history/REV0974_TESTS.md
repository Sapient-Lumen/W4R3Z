# Revision 0974 tests

## Focused resource-boundary lane

```bash
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 pytest -q \
  tests/test_string_preallocation_budget.py \
  tests/test_value_text_budget.py \
  tests/test_string_hostcalls.py \
  tests/test_hostcall_result_budget.py \
  tests/test_plugin_execution_budget.py \
  tests/test_type_predicates_and_conversions.py \
  tests/test_regex_hostcalls.py \
  tests/test_regex_containment.py
```

Result: **108 passed**.

This lane proves exact UTF-8 accounting (including surrogate replacement),
exact-fit acceptance, stack preservation, shared-reference amplification denial,
a 300 MB replacement projection rejected under a Linux address-space ceiling,
bounded giant-integer accounting, bounded `to-str`/`.`/`.s`, regex/query byte
count reuse, and a plugin callback that fails visibly while all host/plugin budget
scopes unwind and the shared VM remains usable.

## Compatibility and owner regressions

```bash
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 pytest -q \
  tests/test_features.py tests/test_smoke.py tests/test_core_registry.py \
  tests/test_vm_callstack.py tests/test_plugin_surface_contract.py \
  tests/test_plugin_reload_recovery.py
```

Result: **67 passed**.

## Structural, generated, and handoff evidence

- `python -m compileall -q src tests tools` — passed.
- `PYTHONPATH=src python tools/mxlint.py` — `mxlint: ok`.
- `PYTHONPATH=src python tools/mxeffects.py --write-help-doc --check-help-doc --check` — passed; generated rev0974 contract contains 23 rows.
- `PYTHONPATH=src python tools/mxaudit.py --check` — passed.
- `PYTHONPATH=src python tools/mxportable.py --quiet` — **157/157** cases passed.
- revision index, context, and living-doc hygiene — **12 passed**.
- effect-contract tests — **5 passed**.
- structural audit tests — **4 passed**.
- Makefile handoff-manifest tests — **6 passed**.
- `tools/mxcontext.py --json --check` — rev0974, 64 documents, no missing paths.
- `tools/mxrelease.py --package-inputs` and JSON form — passed.
- `tests/test_mkrevzip.py` — **52 passed**; the expected duplicate-member rejection test emits one `zipfile` warning.

The first archive-test run correctly failed because the checked-in context still
said rev0973. Regenerating `MICROMAX-CONTEXT.json` from the cleaned rev0974 source
made the lineage sources agree and the complete archive-generator/verifier test
file pass.

## Independent old-path reproduction

Running rev0973 under a Linux address-space ceiling reproduced the pre-fix
failure exactly:

```json
{"message":"","stack_preserved":false,"type":"MicromaxError"}
```

The rev0974 regression under the same policy returns the named 300,000,000-byte
budget denial with all three operands intact.

## Scope of claim

These are focused, compatibility, generated, structural, and archive checks for
the changed boundary. They do not claim a complete repository suite,
hostile-code containment, process memory isolation, universal native-call
cancellation, or all possible large-object traversal limits.

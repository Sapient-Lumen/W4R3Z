# Rev0906 source-load graph budget

Rev0906 turns the rev0905 executable-source budget from a per-file/per-eval
ceiling into a small dependency-graph boundary.  `ed.require` and script-context
core `include` / `require` / `reload` now share VM-tunable include-depth and
cumulative-source-byte limits across one load tree.

## Why this mattered

Rev0905 made each executable source file size-bounded and gave each loaded source
a nested VM step budget.  That still left a graph-shaped resource path: a tiny
root source could include many individually small files, and each individual file
would pass the per-file cap.  That is exactly the sort of "number of operations"
and parameter-controlled resource consumption OWASP API4:2023 warns about:
limits need to cover execution time, memory, operation counts, record counts, and
payload sizes together rather than relying on one cap.  WASI's current capability
model points the same direction for future isolation work: modules begin with no
ambient authority and only receive host grants explicitly supplied by the host.

Online sources used for this cut:

- OWASP API4:2023 Unrestricted Resource Consumption —
  https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- WASI introduction and capability-based sandbox statement —
  https://wasi.dev/
- Python.org sandboxing discussion warning that in-process Python sandboxing is
  not the right security boundary for hostile code —
  https://discuss.python.org/t/extending-subinterpreters-with-sandboxing-capabilities/45355

The product lesson is narrow: this is not a hostile-code sandbox.  It is a
stronger in-process budget around an approved source-load operation so one
approved file cannot quietly become an unbounded dependency ingest.

## What changed

- `hostcall_boundary.py` now also exposes
  `DEFAULT_SOURCE_LOAD_MAX_DEPTH`, `DEFAULT_SOURCE_LOAD_MAX_TOTAL_BYTES`,
  `effective_source_load_max_depth()`, and
  `effective_source_load_max_total_bytes()`.
- `install_editor_hostcalls()` installs the new defaults as
  `editor_source_load_max_depth` and `editor_source_load_max_total_bytes`.
- `micromax.core` owns a small shared source-load graph frame:
  `source_load_graph_frame()`, `source_load_record_bytes()`, and
  `source_text_byte_count()`.
- Standalone VMs keep historical loader behavior unless an embedding installs
  the editor source-load attributes.
- `ed.require` enters the graph frame before resolving/reading/evaluating its
  root source, records the root source byte count before stack consumption, and
  still preserves the direct path operand if the graph budget rejects the load.
- Script-context core `include`, `require`, and `reload` enter the same graph
  frame, so nested plugin-private includes count against the root `ed.require`
  tree's active depth and cumulative bytes.
- `mxaudit --check` now hard-checks the graph-budget seam separately from the
  prior per-file/per-eval `source_load_eval_budget` seam.

## Audit/refactor note

This is deliberately not a source-loader registry.  The refactor is a small
shared VM helper in `micromax.core` because core loader words must enforce the
same graph state that the editor bridge starts.  The editor boundary module owns
the default dials; the core helper only observes attributes already installed by
an embedding.  That keeps ordinary standalone Micromax runs unchanged while
making editor-owned code loads cumulative.

A small test-hygiene fix also landed while validating the lane: the duplicate
query-budget tests in `tests/test_editor_require_caps.py` now have the same
`_call_host()` helper and `limit=`-accepting stub shape as the canonical
hostcall-boundary tests, so the focused require/capability file can run cleanly
again.

## Evidence

Focused evidence for rev0906:

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_require_caps.py
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_require_caps.py tests/test_plugin_containment_and_caps.py tests/test_editor_plugin_manual_load_grants.py tests/test_mxaudit.py
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_mxcontext.py tests/test_revision_index.py tests/test_docs_living_hygiene.py
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxlint.py
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxaudit.py --check
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxcontext.py --check
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxportable.py --quiet
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxtimely.py --skip-doctor --skip-tests --summary-json .artifacts/mxtimely-summary.json
```

The focused suite covers:

- nested `include` under `ed.require` failing on `editor_source_load_max_depth`
  before the helper source evaluates;
- cumulative source bytes failing when a root file plus nested helper exceeds
  `editor_source_load_max_total_bytes` even though each file is individually
  below `editor_source_load_max_bytes`;
- direct root graph-byte rejection preserving the `ed.require` path operand and
  skipping source evaluation;
- existing per-file byte and nested eval-step failures still passing;
- plugin containment/manual-load grant tests still passing with the shared graph
  frame installed;
- audit output and hard-check coverage for `source_load_graph_budget`.

## Remaining risk

This is still instruction-count and byte/depth accounting inside one process.  It
is not wall-clock cancellation for blocking hostcalls, native work, or memory
pressure inside Python objects.  The next high-risk runtime lane is wall-clock
cancellation for expensive per-row builders and any remaining host operations
where one allowed candidate can still do costly work after count budgets fire.

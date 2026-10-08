# Rev0940 — generated effect/resource contract slice

## What changed

Rev0940 lands the first executable effect/resource contract slice instead of
adding another static doctrine table.

`src/micromax_editor/effect_contracts.py` now generates
`micromax.effect-resource-contract.v1` rows from live source facts:

- editor hostcall names and handlers from `EDITOR_HOSTCALL_REGISTRY`;
- capability options/docs from `CAPS`;
- resource defaults from `hostcall_boundary.py`, `host_limits.py`,
  `host_regex.py`, and `stdlib_resource.py`;
- optional audit evidence from the existing `mxaudit` runtime-policy payload.

The initial scope is intentionally narrow and high-risk: filesystem read/list/stat,
file open/save, shell process execution, source load/eval, external clipboard
import, regex hostcalls, and the bundled stdlib package-resource read/eval. The
CLI `tools/mxeffects.py --json --check` emits and validates the slice, `make
effect-contracts` exposes it, `tools/mxaudit.py --check` consumes the generated
payload as a hard audit-integrity check, and `tools/mxcontext.py` now points
future sessions at the contract generator.

This is not a sandbox and not a final plugin API. It is the first bridge from
scattered resource-boundary work to machine-readable contract truth.

## Why this was next

Rev0939 identified the core missing piece: the repo had many strong local
resource and owner seams, but the facts were spread across revision notes, tests,
`mxaudit` string predicates, source constants, and large hostcall bodies. That
made future work risky because a session could keep adding prose or one-off audit
booleans while never producing the living effect/resource contract the mission
requires.

The correction was to generate a small slice from live code rather than write a
large manual matrix. A static spreadsheet of host effects would immediately
become another stale registry. A generated row that refuses stale handler,
capability, and default-budget facts is smaller, more honest, and easier to
expand one effect family at a time.

## Online research used

Current OWASP API4:2023 guidance frames unrestricted resource consumption around
missing or inappropriate limits for execution time, memory, process/file counts,
request payload size, operation counts, and record counts. The contract therefore
surfaces byte, row, cell, timeout, process-output, source-depth, and evaluation
step budgets as first-class fields instead of burying them in prose:
https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/

Python's subprocess documentation warns that process creation itself may not be
interruptible even when timeouts are specified, while `subprocess.run()` kills
and waits for the child only after the timeout is observed. That reinforces the
need for the shell and clipboard-process rows to name both timeout and output
budgets, and not imply a perfect process sandbox:
https://docs.python.org/3/library/subprocess.html

The WebAssembly Component Model WIT documentation says WIT defines interfaces and
worlds as contracts between components, not behavior; its resource guide frames
resources as functionality implemented on one side of a component boundary. That
is a useful future shape for Micromax, but only after native host-effect facts
are already generated and small:
https://component-model.bytecodealliance.org/design/wit.html
https://component-model.bytecodealliance.org/using-wit-resources.html

Starlark remains a useful comparator because it is a small embedded language and
its specification describes deterministic, hermetic execution where user code
cannot interact with the environment by default. Micromax differs by being
concatenative and editor-hosted, but the lesson is the same: host effects must be
explicit and contract-backed:
https://starlark-lang.org/
https://starlark-lang.org/spec.html

## Audit/refactor notes

The new generator deliberately keeps code facts close to their owners:

- `effect_contracts.py` imports constants and registries directly; it does not
  scrape docs.
- The contract validates that each scoped editor hostcall still exists in the
  hostcall registry and that its capability option still matches `CAPS`.
- Regex rows use the VM-hostcall constants and the shared hostcall-result budget,
  not editor-only capability rows.
- The stdlib row uses `stdlib_resource_contract()` so package-resource authority
  and byte ceiling stay owned by the stdlib resource module.
- `mxaudit` passes its runtime-policy facts into the generator and fails if the
  generated payload has stale/missing rows.

This is a refactor of audit truth, not another paper checklist. The high-risk
resource rows now have one CLI surface that embedders, docs, and future installed
help can consume.

## Tests and audit

Focused validation for the new contract slice:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_effect_contracts.py tests/test_mxaudit.py tests/test_mxcontext.py
```

Result: 10 passed.

Contract CLI validation:

```bash
PYTHONPATH=src python tools/mxeffects.py --json --check
PYTHONPATH=src python tools/mxeffects.py --check
```

Result: both passed; the JSON payload reported 14 contract rows and no errors.

## Remaining risk

This initial contract is a slice, not the complete owner graph. It covers the
most visible high-risk host effects but does not yet enumerate every editor
hostcall, every prompt/model scan surface, every delayed plugin-owned resource,
or every durable/rollback behavior. Some fields still describe recovery in broad
language because the underlying effect families do not yet share one typed
journal.

The next expansion should not add a manual catalog. It should derive more rows
from owner methods and focused tests: active-search/register ownership is still a
strong candidate only if the slice removes a concrete stale lifetime, authority
clobber, retention, or rollback failure. A second good step is to let installed
help render selected contract rows so users can inspect effect authority without
reading revision notes.

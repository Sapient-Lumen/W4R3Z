# Rev0941 — active-search owner contract row

## What changed

Rev0941 turns active-search rollback from an ambient private runtime tuple into an
editor-owned authority seam and makes that seam visible in the generated
contract.

`ActiveSearchRegisterSnapshot` is now the editor-owned snapshot for the active
search register. `Editor.snapshot_search_group_state()` /
`restore_search_group_state()` and `Editor.snapshot_search_generation_state()` /
`restore_search_generation_state()` capture, clear, and restore both the search
query and its `RuntimeRegistrationAuthority` provenance. `plugin_runtime.py`
uses those owner methods for group cleanup, generation cleanup, and broad
registration fallback before falling back to the legacy tuple helpers for
alternate embedders.

The generated effect/resource contract now includes
`ed.active-search-register` as an `editor-owner` row with `cap.search-read` and
`cap.search-replay` as the authority-bearing capabilities. `mxaudit --check`
reports and enforces `active_search_owner_snapshot_present`, while
`tools/mxeffects.py --json --check` validates the owner method facts alongside
the existing host-effect rows.

## Why this was next

Rev0940 deliberately left owner rows out of the first contract slice until there
were live owner methods and focused route tests. Active search was the right next
candidate because it is small, concrete, and risky: a plugin-created search query
can outlive the callback or plugin generation that created it, then later move
the user's cursor through find-next/find-prev. That is delayed navigation
authority, not just display state.

Before this change, the runtime's broad/group/generation paths still knew how to
snapshot and restore the active search tuple directly. That was wasteful and
fragile for the same reason earlier clipboard, macro, keymode, prompt,
query-replace, and pending-open-url paths were fragile: cleanup policy lived in
both the editor and the runtime. Rev0941 moves the in-tree primary path to the
editor owner and leaves raw tuple access as an alternate-embedder fallback.

## Online research used

CWE-400 frames uncontrolled resource consumption as a failure to track and
restrict resource use; CWE-770 distinguishes bounded allocation from closely
related lifetime/resource-management failures. Active search is not CPU-heavy,
but it is a held authority resource whose owner and cleanup scope must be
tracked explicitly:
https://cwe.mitre.org/data/definitions/400.html
https://cwe.mitre.org/data/definitions/770.html

OWASP API4:2023 treats execution time, memory, process/file counts, operation
counts, and record counts as first-class resource limits. The relevant lesson for
Micromax is broader than quotas: host-visible effects and retained resources
need named boundaries, scope, and recovery behavior instead of ambient authority:
https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/

The WebAssembly Component Model WIT resource model remains a useful comparator:
resources are handles to functionality implemented on one side of a boundary.
Micromax is not moving this owner into a Wasm/process boundary yet, but the row
shape should still name the host side, capability side, and lifecycle side:
https://component-model.bytecodealliance.org/using-wit-resources.html

## Audit/refactor notes

This was intentionally more than a registry edit:

- The editor owns capture/restore semantics for active-search query and authority
  provenance.
- Runtime cleanup now calls owner methods for group, generation, and broad
  registration rollback, reducing direct coupling to editor private state.
- Focused regressions monkeypatch the owner methods to prove the runtime routes
  through them.
- `mxaudit` checks the editor owner methods, runtime routing, broad fallback
  routing, human output, and focused tests.
- `effect_contracts.py` introspects the live editor methods and capability
  registry to generate the `ed.active-search-register` row.

The value is a real owner-boundary migration plus generated evidence, not another
manual doctrine table.

## Tests and audit

Focused validation for the owner route and generated contract:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_plugin_runtime_group_policy.py tests/test_effect_contracts.py tests/test_mxaudit.py
```

Result: passed.

Contract and audit validation:

```bash
PYTHONPATH=src python tools/mxeffects.py --json --check
PYTHONPATH=src python tools/mxaudit.py --json --check
```

Result: both passed; the generated contract now reports 15 rows, including
`ed.active-search-register`, with no validation errors.

## Remaining risk

The generated owner row is still one resource family. Other delayed owner
surfaces, durable editor state, document edits, external effects, and crash
behavior are still not unified into one complete effect/lifecycle contract. The
next work should stay behavior-backed: add owner rows only where code can expose
real owner methods and tests, and avoid growing a manual registry ahead of the
runtime truth.

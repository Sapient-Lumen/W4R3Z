# Query-replace owner snapshot (rev0933)

Rev0933 continues the active-interaction owner work with the smallest adjacent
runtime seam: the live query-replace session row. Rev0931 bounded `qreplace all`
so one response cannot become an unbounded foreground edit sweep, but runtime
cleanup and rollback still treated `Editor.qreplace` and the cursor/selection
state around it as separate pieces. This revision makes query-replace a single
editor-owned delayed interaction object for group/generation snapshot and
restore.

## External check

The online check stayed deliberately narrow and used the same vocabulary as the
prior active-interaction slice:

- MITRE CWE-772, Missing Release of Resource after Effective Lifetime:
  <https://cwe.mitre.org/data/definitions/772.html>
- OWASP API4:2023, Unrestricted Resource Consumption:
  <https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/>

For Micromax, the translation is concrete: a delayed interaction has an
effective lifetime and should have one owner for capture, clear, and restore.
Query-replace is especially risky because it combines authority, a live response
budget, the active buffer, and visible selection/cursor state. Restoring only the
session while leaving the visible selection behind, or clearing only the session
while leaving stale capture state, is the kind of slow drift that turns rollback
into surprise behavior.

## What changed

- Added `QueryReplaceInteractionSnapshot` and
  `QueryReplaceInteractionCursorSnapshot` in `editor.py` as the editor-owned
  value objects for query-replace delayed interaction state.
- Added editor owner methods for group and generation snapshot/restore:
  `snapshot_qreplace_group_state()`, `restore_qreplace_group_state()`,
  `snapshot_qreplace_generation_state()`, and
  `restore_qreplace_generation_state()`.
- Centralized query-replace cleanup in `_clear_qreplace_runtime_row()`, which
  clears the session and visible primary selection together.
- Refactored `plugin_runtime.py` group/generation interaction snapshot and
  restore to call the owner methods instead of reading or writing
  `Editor.qreplace` directly.
- Kept the existing runtime snapshot shape compatible by storing the owner
  session/cursor payloads in the existing `qreplace` and `qreplace_cursor`
  fields.
- Added focused regressions that monkeypatch the editor owner methods and prove
  runtime group/generation snapshot+restore routes through them.
- Extended `tools/mxaudit.py --check` with
  `qreplace_owner_snapshot_present=True` and human output
  `qreplace-owner=True`.

## Audit/refactor value

This removes another direct field family from the active-interaction
snapshot/restore hot path without starting a broad registry. The runtime wrapper
still coordinates the transaction, but the editor now owns the semantics of a
query-replace row: capture the session with the visible cursor state, clear it
as a coupled row, and restore it only through owner methods.

The result is intentionally not a huge architecture rewrite. It is one more
small executable owner contract, adjacent to rev0932's open-URL owner and
rev0931's query-replace response budget.

## Validation

Run from the repository root:

```sh
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  pytest -q tests/test_plugin_runtime_group_policy.py tests/test_mxaudit.py

PYTHONPATH=src python tools/mxaudit.py --check --limit 3

PYTHONPATH=src python tools/mxlint.py
```

Observed in the rev0933 cloudtainer before packaging:

- `tests/test_plugin_runtime_group_policy.py tests/test_mxaudit.py`: `43 passed, 13 warnings`
- revision-index/docs/context/audit focused selector (`tests/test_revision_index.py tests/test_docs_living_hygiene.py tests/test_mxcontext.py tests/test_plugin_runtime_group_policy.py tests/test_mxaudit.py`): `52 passed, 13 warnings`
- `tools/mxaudit.py --check --limit 3`: clean check with `qreplace-owner=True`
- `tools/mxcontext.py --check`: clean context check for rev0933
- `tools/mxlint.py`: `mxlint: ok`

## Remaining risk

- Prompt interaction snapshot/restore still reaches through direct prompt fields
  and remains the next active-interaction owner candidate.
- Broad failed-callback interaction snapshot still stores the whole interaction
  state directly for compatibility.
- Query-replace is now owner-routed for runtime cleanup/rollback, but this does
  not turn the in-process plugin model into OS sandboxing, memory isolation, or
  malicious-code containment.

# Rev0944 — saved-cursor owner contract row

## What changed

Rev0944 moves saved-cursor rollback from raw runtime dictionary/authority sidecar
rewrites into an editor-owned retained cursor owner seam and makes that seam
visible in the generated effect/resource contract.

`SavedCursorRegisterEntry` and `SavedCursorRegisterSnapshot` are now the
editor-owned value objects for authority-stamped saved-cursor rows. Each row
carries the retained path, line, column, and `RuntimeRegistrationAuthority` that
created it. `Editor.snapshot_saved_cursor_group_state()` /
`restore_saved_cursor_group_state()` and
`Editor.snapshot_saved_cursor_generation_state()` /
`restore_saved_cursor_generation_state()` capture, drop, and restore only the
matching rows while preserving unrelated trusted/user rows. `plugin_runtime.py`
uses those owner methods for runtime-group cleanup, generation cleanup, and
broad registration restore before the legacy raw `_saved_cursors` fallback is
reachable for alternate editor hosts.

The generated effect/resource contract now includes `ed.saved-cursor-register`
as an `editor-owner` row with `ed.cursor-restore` and `ed.persist` as the
observed authority-bearing capabilities. `mxaudit --check` reports and enforces
`saved_cursor_owner_snapshot_present`, and `tools/mxeffects.py --json --check`
validates the owner method facts alongside the active-search, prompt-history,
recent-files, and high-risk host-effect rows.

## Why this was next

Saved cursors are not just convenience state. A saved-cursor row retains a
filesystem path plus an exact file position and can be persisted through
`savecursor.file` / `cap.persist`; later it can steer a user or script back to
that path and location. That makes it retained path+position navigation
authority.

Before this change, runtime cleanup still had primary broad snapshot/restore
paths that copied `_saved_cursors` and `_saved_cursors_authority` directly. That
split ownership between the editor, which understands saved-cursor persistence
and cursor-restore policy, and the runtime, which should only know that a
resource family has a lifecycle owner. Rev0944 removes that primary-path
duplicate policy and leaves raw sidecar handling only in the narrow helper
fallback for alternate embedders or older snapshots.

## Online research used

OWASP API4:2023 is still the relevant cloudtainer warning: boundaries are not
just permission checks, they also need explicit limits and owners for resources
that can be retained or consumed over time:
https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/

MITRE CWE-200, CWE-359, CWE-497, and CWE-1230 frame why path/location metadata
should not be treated as harmless UI data. Even without reading file bytes, a
retained path or derived location can disclose system, project, or private user
information when replayed, logged, exposed, or persisted:
https://cwe.mitre.org/data/definitions/200.html
https://cwe.mitre.org/data/definitions/359.html
https://cwe.mitre.org/data/definitions/497.html
https://cwe.mitre.org/data/definitions/1230.html

The Python copy documentation is a useful reminder for snapshot code: assignment
only binds objects, shallow copies retain nested references, and indiscriminate
deep copies can copy too much. The saved-cursor owner seam therefore normalizes
path/line/column rows explicitly instead of relying on ambient dictionary copies:
https://docs.python.org/3/library/copy.html

VS Code Workspace Trust remains a practical comparator for editor hosts: code
loaded from a workspace can create delayed effects, so trusted/restricted
feature surfaces need to be explicit and disableable rather than implicit shared
state:
https://code.visualstudio.com/api/extension-guides/workspace-trust

## Audit/refactor notes

This landing was intentionally behavior-backed:

- The editor now owns saved-cursor row capture/restore for runtime groups and
  plugin generations.
- Runtime group rollback, generation rollback, and broad registration restore
  call the owner seam first.
- The focused tests monkeypatch the editor owner methods to prove the runtime
  uses them for runtime-group, broad registration, and plugin-generation
  rollback.
- `mxaudit` checks the editor value objects, owner methods, runtime routing,
  broad restore route, human output, focused tests, and generated contract row.
- `effect_contracts.py` introspects the live editor methods, audit evidence,
  and capability registry to generate `ed.saved-cursor-register`.

The waste corrected here was a duplicate hidden lifecycle policy: broad cleanup
could still rewind retained cursor path rows by hand even though the editor held
the persistence and authority model.

## Tests and audit

Focused validation for the owner route and generated contract:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q \
  tests/test_plugin_runtime_group_policy.py::test_runtime_group_saved_cursor_snapshot_restore_uses_editor_owner \
  tests/test_plugin_runtime_group_policy.py::test_broad_registration_saved_cursor_snapshot_restore_uses_editor_owner \
  tests/test_plugin_runtime_group_policy.py::test_runtime_generation_saved_cursor_snapshot_restore_uses_editor_owner \
  tests/test_plugin_runtime_group_policy.py::test_runtime_generation_snapshot_scopes_nonmacro_delayed_rows
```

Contract and audit validation:

```bash
PYTHONPATH=src python tools/mxeffects.py --json --check
PYTHONPATH=src python tools/mxaudit.py --json --check
```

The archive validation also used `mxlint`, `mxcontext --check`, `make timely`,
and archive verification.

## Remaining risk

The generated owner contract now covers active search, prompt history, recent
files, and saved cursors. It still is not a full effect/lifecycle graph. Palette
MRU, marks, recovery stacks, help history, document edits, durable external
effects, crash behavior, memory pressure, native code, and hostile-code
containment remain outside a unified owner contract. The next migration should
remain behavior-backed: choose the next survivor only if route tests can prove a
stale lifetime, authority clobber, retained disclosure, or rollback failure.

# Rev0945 — palette-recent owner contract row

## What changed

Rev0945 moves command-palette recent-row rollback from raw runtime
`_palette_recent` / `_palette_recent_authority` list rewrites into an
editor-owned retained command/action launch owner seam and makes that seam
visible in the generated effect/resource contract.

`PaletteRecentRegisterEntry` and `PaletteRecentRegisterSnapshot` are now the
editor-owned value objects for authority-stamped command-palette MRU rows. Each
row carries the visible row kind, command/action name, original position, and
`RuntimeRegistrationAuthority` that created it. `Editor.snapshot_palette_recent_group_state()` /
`restore_palette_recent_group_state()` and
`Editor.snapshot_palette_recent_generation_state()` /
`restore_palette_recent_generation_state()` capture, drop, and restore only the
matching rows while preserving unrelated trusted/user rows. `plugin_runtime.py`
uses those owner methods for runtime-group cleanup, generation cleanup, and
broad registration restore before the legacy raw `_palette_recent` fallback is
reachable for alternate editor hosts.

The generated effect/resource contract now includes
`ed.palette-recent-register` as an `editor-owner` row with `ed.command-read`,
`ed.action-read`, and `ed.history-clear` as the observed authority-bearing
capabilities. `mxaudit --check` reports and enforces
`palette_recent_owner_snapshot_present`, and `tools/mxeffects.py --json --check`
validates the owner method facts alongside the active-search, prompt-history,
recent-files, saved-cursor, and high-risk host-effect rows.

## Why this was next

Command-palette recent rows are not just visual sorting hints. They are retained
launch affordances for commands and actions. A plugin-created row can survive
unload/reload and later keep a stale command or action near the top of the
user's launcher, even after the plugin generation that created the row has been
retired or replaced. That makes palette MRU a retained command/action authority
surface, not a cosmetic preference.

Before this change, the runtime still copied `_palette_recent` and
`_palette_recent_authority` directly in primary broad snapshot/restore paths.
That split ownership between the editor, which understands palette visibility,
command/action read capabilities, and authority sidecars, and the runtime, which
should only know that a resource family has a lifecycle owner. Rev0945 removes
that primary-path duplicate policy and leaves raw sidecar handling only in the
narrow helper fallback for alternate embedders or older snapshots.

## Online research used

MITRE CWE-404 frames improper resource shutdown/release as a security problem,
not just a cleanup detail: insufficient tracking and error handling can cause
resources to remain available too long or be released incorrectly.
https://cwe.mitre.org/data/definitions/404.html

OWASP API4:2023 remains the relevant cloudtainer warning that a boundary must
include resource limits and resource ownership, not only authorization checks.
https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/

VS Code Workspace Trust is a practical editor-host comparator: extension
features, commands, and other UI-contributed surfaces must be scoped or disabled
when trust is restricted, because a launch affordance can be part of the trust
boundary rather than neutral UI.
https://code.visualstudio.com/docs/editing/workspaces/workspace-trust
https://code.visualstudio.com/api/extension-guides/workspace-trust

## Audit/refactor notes

This landing was intentionally behavior-backed:

- The editor now owns palette-recent row capture/restore for runtime groups and
  plugin generations.
- Runtime group rollback, generation rollback, and broad registration restore
  call the owner seam first.
- The focused tests monkeypatch the editor owner methods to prove the runtime
  uses them for runtime-group, broad registration, and plugin-generation
  rollback.
- `mxaudit` checks the editor value objects, owner methods, runtime routing,
  broad restore route, human output, focused tests, and generated contract row.
- `effect_contracts.py` introspects the live editor methods, audit evidence,
  and capability registry to generate `ed.palette-recent-register`.

The waste corrected here was a duplicate hidden lifecycle policy: broad cleanup
could still rewind command-palette launch rows by hand even though the editor
held the command/action visibility and authority model.

## Tests and audit

Focused validation for the owner route and generated contract:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q \
  tests/test_plugin_runtime_group_policy.py::test_runtime_group_palette_recent_snapshot_restore_uses_editor_owner \
  tests/test_plugin_runtime_group_policy.py::test_broad_registration_palette_recent_snapshot_restore_uses_editor_owner \
  tests/test_plugin_runtime_group_policy.py::test_runtime_generation_palette_recent_snapshot_restore_uses_editor_owner
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
files, saved cursors, and palette recent rows. It still is not a full
effect/lifecycle graph. Marks, recovery stacks, help history, document edits,
durable external effects, crash behavior, memory pressure, native code, and
hostile-code containment remain outside a unified owner contract. The next
migration should remain behavior-backed: choose the next survivor only if route
tests can prove a stale lifetime, authority clobber, retained disclosure, or
rollback failure.

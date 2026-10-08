# Rev0946 help-history owner contract

## Why this was the riskiest next cut

Help history is retained navigation authority, not just UI memory. A plugin can
create help-doc rows that later drive `helpback`, `helpforward`, or `helpresume`
into a docs target and cursor position after unload/reload. Before this revision,
primary cleanup paths still relied on raw `_help_stack`, `_help_forward_stack`,
`_help_session_entry`, and authority-sidecar rewrites for broad registration and
fallback restore.

The online check reinforced treating this as a lifecycle/security seam rather
than cosmetic history cleanup: MITRE CWE-404 describes improper resource
release/tracking as a source of resource exhaustion and confidentiality impact,
and the VS Code Workspace Trust extension guide treats extension-contributed
features as trust-sensitive surfaces that should be disabled or limited in
restricted contexts. Help navigation rows are smaller than processes or files,
but the same owner rule applies: retained, plugin-influenced state should have a
single owner, a scoped rollback contract, and executable audit evidence.

## What changed

- Added `HelpHistoryRegisterEntry` and `HelpHistoryRegisterSnapshot` as
  editor-owned value objects for help back/forward/session rows plus
  `RuntimeRegistrationAuthority`.
- Added `Editor.snapshot_help_history_group_state` /
  `restore_help_history_group_state` for runtime-group cleanup and retag
  rollback.
- Added `Editor.snapshot_help_history_generation_state` /
  `restore_help_history_generation_state` for plugin root/generation cleanup.
- Refactored `plugin_runtime.py` so group, generation, and broad registration
  rollback call the editor owner seam first; raw stack/authority handling remains
  only as alternate-embedder fallback.
- Added the generated `ed.help-history-register` owner row to
  `src/micromax_editor/effect_contracts.py`, derived from live owner methods,
  capability facts, budgets, and audit evidence.
- Extended `mxaudit --check` with `help_history_owner_snapshot_present` and
  human output `help-history-owner=True`.
- Added focused owner-route regressions for runtime group rollback, broad
  registration restore, and generation cleanup restore.

## Audit/refactor result

This removes one more private-state survivor from the in-tree primary rollback
path. Runtime code still has compatibility fallback for alternate embedders, but
`mxaudit --check` now rejects regressions where the primary editor path stops
using the owner seam or where focused route tests disappear.

The generated effect/resource contract now has owner rows for active search,
prompt history, recent files, saved cursors, palette recent rows, and help
history. That is still not the whole effect graph, but it is a real executable
contract slice across the highest-risk retained delayed-state families.

## Validation

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_plugin_runtime_group_policy.py -k 'help_history and owner'`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_effect_contracts.py`
- `PYTHONPATH=src python tools/mxaudit.py --check`
- `PYTHONPATH=src python tools/mxeffects.py --json --check`

Broader validation is recorded by the rev0946 package evidence.

## Remaining risks

- The generated contract is still row-oriented. It does not yet express a typed
  owner graph with effect phases, crash semantics, or cross-owner ordering.
- Alternate embedders can still rely on legacy raw help-history fallback paths.
  The audit guards the in-tree primary editor route.
- Document edits, arbitrary new buffers, external I/O, memory exhaustion, native
  code, and hostile-code containment remain outside this rollback contract.
- The next high-leverage improvement is not another prose registry. It is either
  rendering selected generated contract rows in installed help or consolidating
  the repeated owner-route fallback code once enough rows share the pattern.

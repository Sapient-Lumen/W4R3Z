# Rev0947 recovery owner contract

## Why this was the riskiest next cut

Recovery state is retained navigation authority. Selection-stack and jump-list
rows hold cursor selections, anchors, IDs, jump positions, and a sidecar
`RuntimeRegistrationAuthority`; plugin-owned rows can continue to steer later
navigation after unload/reload unless rollback and cleanup treat them as an
owned resource. Before this revision, the runtime still had primary paths that
rewrote `EditorBuffer.sel_stack`, `EditorBuffer.jump_list`, and their authority
sidecars directly for broad restore, group cleanup, and generation cleanup.

The online check reinforced treating this as lifecycle/security work rather than
editor polish. MITRE CWE-404 connects insufficient resource tracking/release to
resource exhaustion and confidentiality impact; OWASP API4:2023 emphasizes that
missing or inappropriate limits on resource consumption can become a concrete
availability/cost risk; and VS Code Workspace Trust frames extension-contributed
features as trust-sensitive surfaces that should be limited in restricted
contexts. Cursor/selection recovery rows are not external I/O, but they are
retained plugin-influenced state; the same rule applies: one owner, scoped
rollback semantics, and executable evidence.

## What changed

- Added `RecoveryRegisterEntry`, `RecoveryBufferRegisterSnapshot`, and
  `RecoveryRegisterSnapshot` as editor-owned value objects for selection-stack
  and jump-list rows plus `RuntimeRegistrationAuthority`.
- Added `Editor.snapshot_recovery_group_state` /
  `restore_recovery_group_state` for runtime-group cleanup and retag rollback.
- Added `Editor.snapshot_recovery_generation_state` /
  `restore_recovery_generation_state` for plugin root/generation cleanup.
- Refactored `plugin_runtime.py` so group, generation, and broad registration
  rollback call the editor owner seam first; raw stack/authority handling remains
  only as alternate-embedder fallback.
- Fixed the full recovery-register restore path so broad restore replaces the
  captured recovery rows instead of appending them to the mutated current rows.
- Added the generated `ed.recovery-register` owner row to
  `src/micromax_editor/effect_contracts.py`, derived from live owner methods,
  capability facts, budgets, and audit evidence.
- Extended `mxaudit --check` with `recovery_owner_snapshot_present` and human
  output `recovery-owner=True`.
- Added focused owner-route regressions for runtime group rollback, broad
  registration restore, and generation cleanup restore.

## Audit/refactor result

This removes another private-state survivor from the in-tree primary rollback
path and catches a row-duplication bug that only appears when broad restore uses
full recovery-register snapshots after mutation. The compatibility fallback is
still present for alternate embedders, but `mxaudit --check` now rejects the
primary path if it stops routing through the editor owner seam or loses the
focused route tests.

The generated effect/resource contract now has owner rows for active search,
prompt history, recent files, saved cursors, palette recent rows, help history,
and recovery rows. That is still not the complete effect graph, but it is a
substantive executable contract slice over retained editor state that can survive
plugin lifecycle transitions.

## Validation

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_plugin_runtime_group_policy.py::test_runtime_group_recovery_snapshot_restore_uses_editor_owner tests/test_plugin_runtime_group_policy.py::test_runtime_generation_recovery_snapshot_restore_uses_editor_owner tests/test_plugin_runtime_group_policy.py::test_broad_registration_recovery_snapshot_restore_uses_editor_owner`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_effect_contracts.py tests/test_mxaudit.py`
- `PYTHONPATH=src python tools/mxaudit.py --check`
- `PYTHONPATH=src python tools/mxeffects.py --json --check`

Broader validation is recorded by the rev0947 package evidence.

## Remaining risks

- The generated contract is still row-oriented. It does not yet express a typed
  owner graph with effect phases, crash semantics, or cross-owner ordering.
- Alternate embedders can still rely on legacy raw recovery fallback paths. The
  audit guards the in-tree primary editor route.
- Document edits, arbitrary new buffers, external I/O, memory exhaustion, native
  code, and hostile-code containment remain outside this rollback contract.
- The next high-leverage improvement should either render selected generated
  contract rows in installed help or consolidate repeated owner-route fallback
  code only after the shared helper can preserve the proven group/generation
  semantics.

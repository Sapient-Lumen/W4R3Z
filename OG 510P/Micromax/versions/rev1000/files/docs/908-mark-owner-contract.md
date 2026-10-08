# Rev0950 — mark owner contract

## Why this was the riskiest next cut

Named marks are retained navigation authority. A plugin-owned mark records a
buffer name and cursor location, can be listed through mark-read surfaces, and
can later move the editor through mark-jump behavior after plugin unload/reload
unless rollback treats it as owned state. Before this revision, the runtime's
primary broad and scoped rollback paths still copied `Editor.marks` and
`Editor._mark_authority` directly. That left one more path-shaped navigation
register outside the editor-owned owner-contract lane.

The online check kept the cut practical rather than bureaucratic. MITRE
[CWE-404](https://cwe.mitre.org/data/definitions/404.html) frames poor resource
tracking/release as an availability and confidentiality risk, and VS Code's
[Workspace Trust extension guide](https://code.visualstudio.com/api/extension-guides/workspace-trust)
expects trust-sensitive extension behavior to be limited in untrusted workspaces.
Marks are in-process editor state, not an OS sandbox boundary, but plugin-owned
buffer+position records are still retained authority: one owner seam, scoped
restore semantics, and executable audit evidence are warranted.

## Landed change

- Added `MarkRegisterEntry` and `MarkRegisterSnapshot` editor-owned value
  objects for named marks plus `RuntimeRegistrationAuthority` sidecars.
- Added `Editor.snapshot_mark_group_state` /
  `Editor.restore_mark_group_state` so runtime group cleanup and broad failed
  registration restore can use a public owner seam before legacy fallback.
- Refactored `plugin_runtime.py` so group rollback and broad registration
  rollback prefer the editor-owned mark route instead of directly rewriting
  `marks` / `_mark_authority` in the primary in-tree path.
- Removed a redundant `restore_recent_files_group_state` call from the runtime
  group restore path, closing a small waste/regression hazard found during the
  mark audit.
- Added focused route tests proving scoped and broad rollback call the mark owner
  methods and preserve unrelated trusted/during rows correctly.
- Extended `mxaudit --check` with `mark_owner_snapshot_present` and human output
  `mark-owner=True`.
- Added the generated `ed.mark-register` row to the effect/resource contract,
  derived from live owner methods, mark capability facts, rollback lanes, and
  audit evidence.
- Regenerated the installed `docs/33-effect-resource-contract.md` help surface so
  the mark owner row is visible through runtime help as well as JSON tooling.

## Audit/refactor result

This revision intentionally avoids inventing a universal ownership registry. It
moves one concrete retained authority survivor behind an editor-owned lifecycle
seam and verifies that the runtime's primary paths use it. The legacy raw mark
fallback remains for alternate embedders, but `mxaudit --check` now rejects the
in-tree route if the owner seam, generated row, or focused tests disappear.

The refactor also removed a duplicated recent-files restore call in
`restore_runtime_group_state`. That was not the headline security fix, but it was
exactly the kind of small cloudtainer waste this sequence is meant to remove
while touching the risky lifecycle code.

## Validation

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_plugin_runtime_group_policy.py::test_runtime_group_mark_snapshot_restore_uses_editor_owner tests/test_plugin_runtime_group_policy.py::test_broad_registration_mark_snapshot_restore_uses_editor_owner`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_effect_contracts.py tests/test_mxaudit.py`
- `PYTHONPATH=src python tools/mxeffects.py --write-help-doc --check-help-doc --check`
- `PYTHONPATH=src python tools/mxaudit.py --json --check --limit 5`
- `PYTHONPATH=src python tools/mxlint.py`
- `PYTHONPATH=src python tools/mxcontext.py --check`
- `make timely`

## Remaining risks

- Marks remain in-process editor state and do not provide hostile-code
  containment or process isolation.
- The legacy private fallback remains for alternate embedders until compatibility
  evidence says it can be removed.
- Successful plugin mark writes are still committed editor effects unless a
  future lifecycle contract says otherwise.
- The generated contract is still row-oriented; a typed owner graph with phases,
  crash semantics, and cross-owner ordering remains future work.

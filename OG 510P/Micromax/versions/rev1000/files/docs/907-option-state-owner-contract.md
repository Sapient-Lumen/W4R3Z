# Rev0949 — option state owner contract

## Why this was the riskiest next cut

Option state is configuration authority, not a cosmetic preference bag. Global
options include capability mirrors, persistence knobs, history paths, and
buffer-local policy values that can change what later hostcalls are allowed to
observe or replay. Failed plugin source loads, lifecycle hooks, deinit paths, and
scoped callback rollback already captured option snapshots, but the runtime's
primary path still reached through private editor methods. That made the
configuration rollback seam harder to audit and easier to bypass while the
owner-row contract was moving other retained state behind public editor methods.

The online check kept the cut narrow. MITRE
[CWE-269](https://cwe.mitre.org/data/definitions/269.html) frames improper
privilege management as assigning or preserving privileges in a way that creates
unauthorized access. MITRE
[CWE-404](https://cwe.mitre.org/data/definitions/404.html) connects poor
resource tracking/release to exhaustion and confidentiality failures. VS Code's
[Workspace Trust extension guide](https://code.visualstudio.com/api/extension-guides/workspace-trust)
expects trust-sensitive extension behavior to be disabled or limited until the
workspace is trusted. Micromax options are in-process state rather than an OS
sandbox, but option rollback still needs one owner seam because capability and
persistence values shape future authority.

## Landed change

- Added public `Editor.snapshot_option_state` /
  `Editor.restore_option_state` owner methods that wrap the existing global and
  buffer-local `OptionStateSnapshot` machinery.
- Refactored `plugin_runtime.py` so broad failed source/lifecycle registration
  restore and scoped plugin callback rollback prefer the editor-owned option
  methods before falling back to legacy private methods for alternate embedders.
- Added focused regressions proving broad registration restore and scoped
  callback rollback call the public owner seam and restore option values through
  it.
- Extended `mxaudit --check` with `option_state_owner_snapshot_present` and
  human output `option-owner=True`.
- Added the generated `ed.option-state-register` row to the effect/resource
  contract, derived from live owner methods, `ed.option-read` capability facts,
  rollback lanes, and audit evidence.
- Regenerated the installed `docs/33-effect-resource-contract.md` surface so the
  option-state row is visible through runtime help as well as the JSON contract.

## Audit/refactor result

This is deliberately a small owner seam, not a new universal option registry.
The existing option snapshot value objects still define what gets rolled back;
the runtime now reaches them through a public editor-owned lifecycle method, and
the generated contract/audit path fails if the primary in-tree route stops using
that seam. Successful plugin option changes remain ordinary committed
configuration effects; this revision only narrows failed source/lifecycle and
callback rollback.

## Validation

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_editor_plugin_option_rollback.py`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_effect_contracts.py tests/test_mxaudit.py`
- `PYTHONPATH=src python tools/mxeffects.py --write-help-doc --check-help-doc --check`
- `PYTHONPATH=src python tools/mxaudit.py --json --check --limit 5`
- `PYTHONPATH=src python tools/mxlint.py`
- `PYTHONPATH=src python tools/mxcontext.py --check`
- `make timely`

## Remaining risks

- This does not make successful plugin option writes group- or generation-owned;
  they stay committed configuration effects unless a later contract changes that
  policy.
- Options remain in-process authority, not a hostile-code containment boundary.
- The legacy private fallback remains for alternate embedders until compatibility
  evidence says it can be removed.
- The generated contract still needs a compact shared validation helper before
  more owner rows make `effect_contracts.py` repetitive.

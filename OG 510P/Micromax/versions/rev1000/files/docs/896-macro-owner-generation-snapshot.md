# Macro owner generation snapshot (rev0938)

Rev0938 moves generation-scoped macro rollback behind an editor-owned macro
snapshot/restore seam. Rev0886 made plugin generation cleanup narrow for saved
macro slots and live macro recordings, and rev0893 added stale-generation
playback refusal. Those were the right behavior boundaries, but the rollback
implementation still lived in `plugin_runtime.py` and reconstructed `Editor`
macro internals directly: `macros`, the stable `last` alias list, the live
recording buffer, and recording origin fields.

That was the riskiest remaining delayed-executable seam after active
interaction and clipboard ownership. A saved macro is not passive history: it is
a replayable sequence of editor commands/actions with script/plugin provenance.
A live recording is also delayed executable state, because a plugin callback can
start recording and return before later user or script turns stop, cancel, or
append to it. Runtime cleanup should decide *when* a plugin generation is being
rolled back; the editor should decide *how* macro slots and live recording state
are represented, cleared, and restored.

## External check

The online check stayed tied to the implementation slice:

- MITRE CWE-400, Uncontrolled Resource Consumption:
  <https://cwe.mitre.org/data/definitions/400.html>
- MITRE CWE-770, Allocation of Resources Without Limits or Throttling:
  <https://cwe.mitre.org/data/definitions/770.html>
- OWASP Denial of Service Cheat Sheet:
  <https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html>
- OWASP API4:2023, Unrestricted Resource Consumption:
  <https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/>

The applied rule is narrow: delayed executable resources should have one owner
that can capture and release them over their effective lifetime. For macros,
that owner is the editor because only the editor knows the `last` alias contract,
live recording fields, and authority semantics around macro mutation and replay.

## What changed

- Added `MacroGenerationSlotSnapshot`, `MacroGenerationRecordingSnapshot`, and
  `MacroGenerationSnapshot` in `editor.py`.
- Added `Editor.snapshot_macro_generation_state()` and
  `Editor.restore_macro_generation_state()` as the owner seam for saved macro
  slots and live recording state owned by one plugin root/generation.
- Refactored `plugin_runtime.snapshot_macro_generation_state()` and
  `plugin_runtime.restore_macro_generation_state()` to ask the editor owner
  methods first, while preserving the old raw-field path only as an
  alternate-embedder fallback.
- Kept the generation snapshot narrow: trusted/user macro slots are not rewound
  when plugin-generation cleanup fails, and the stable `last` list remains the
  editor's alias invariant.
- Added a focused route regression that monkeypatches the editor owner methods
  and proves generation snapshot/restore goes through that seam.
- Extended `tools/mxaudit.py --check` and human output with
  `macro_owner_generation_snapshot_present=True` / `macro-owner=True`.

## Audit/refactor value

This is intentionally not a new registry. It removes one raw-state coupling
from the runtime rollback path where a partial plugin unload/reload failure can
otherwise lose or resurrect delayed executable state. It also makes the boundary
more honest: plugin runtime still owns lifecycle transaction decisions, but it
no longer has to duplicate the editor's macro registry invariants.

The fallback path remains because `plugin_runtime.py` can be reused by alternate
hosts, but the in-tree editor now takes the owner path and the audit checks that
primary route.

## Validation

Run from the repository root:

```sh
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  pytest -q tests/test_plugin_runtime_group_policy.py

PYTHONPATH=src python tools/mxaudit.py --check
PYTHONPATH=src python tools/mxcontext.py --check
PYTHONPATH=src python tools/mxlint.py
```

Observed in the rev0938 cloudtainer before packaging:

- `tests/test_plugin_runtime_group_policy.py` plus audit JSON selector: `50 passed, 13 warnings`
- living docs/context selectors: `9 passed`
- selected mkrevzip context/verification selectors: `2 passed`
- `tools/mxaudit.py --check`: clean check with `macro-owner=True`
- `tools/mxcontext.py --check`: clean context for rev0938
- `tools/mxlint.py`: `mxlint: ok`

## Remaining risk

- Broad `RuntimeRegistrationSnapshot` still restores macro state directly for
  plugin source/lifecycle/deinit failure fallback. That path is broader because
  failed plugin code can overwrite arbitrary macro slots; move it only with a
  concrete test that proves reduced clobber or retention behavior.
- Active search remains the next plausible singleton owner candidate because it
  carries search payload plus authority sidecar and has group/generation paths.
- Prompt history, saved cursors, recent files, and palette MRU remain mixed
  row-shaped owner/fallback seams; they are less risky than delayed executable
  macros unless a stale-authority or partial-restore bug appears.
- This remains an in-process application boundary, not OS sandboxing, memory
  isolation, native-code containment, or protection from malicious plugins.

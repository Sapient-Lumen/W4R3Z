# Plugin callback interaction owner (rev0936)

Rev0936 removes the broad failed-callback interaction snapshot from raw runtime
field access. Rev0932-0935 moved group/generation rollback for pending open-url,
query-replace, prompt, and keymode rows to editor-owned methods. The remaining
compatibility fallback was `plugin_runtime.snapshot_editor_interaction_state()`:
it still read and restored `Editor.prompt`, `Editor.qreplace`,
`Editor.key_mode_stack`, pending-open-url fields, and input scratch directly when
a failed plugin callback used the broad registration snapshot.

That was the riskiest unfinished slice because callback rollback is the
last-ditch path after deferred plugin code has already run and raised. If it
splits lifetime semantics across raw runtime glue and editor owner methods, the
next interaction feature can regress into half-restored delayed authority.

## External check

The online check stayed implementation-bound:

- MITRE CWE-664, Improper Control of a Resource Through its Lifetime:
  <https://cwe.mitre.org/data/definitions/664.html>
- MITRE CWE-400, Uncontrolled Resource Consumption:
  <https://cwe.mitre.org/data/definitions/400.html>
- MITRE CWE-772, Missing Release of Resource after Effective Lifetime:
  <https://cwe.mitre.org/data/definitions/772.html>

The applied rule is small: delayed interaction resources need one owner for
create/use/release and rollback over their effective lifetime. For broad failed
plugin callbacks, the owner is now one editor aggregate, not five raw fields in
runtime code.

## What changed

- Added `PluginCallbackInteractionSnapshot` in `editor.py` as the editor-owned
  aggregate for full failed-callback delayed interaction state.
- Added `Editor.snapshot_plugin_callback_interaction_state()` and
  `Editor.restore_plugin_callback_interaction_state()`.
- Composed the aggregate out of existing owner snapshots:
  `snapshot_key_mode_group_state(None)`, `snapshot_prompt_group_state(None)`,
  `snapshot_qreplace_group_state(None)`, and
  `snapshot_pending_open_url_group_state(None)`, plus bounded input scratch copy.
- Refactored `plugin_runtime.snapshot_editor_interaction_state()` and
  `restore_editor_interaction_state()` to call the editor aggregate owner method
  instead of directly reading or rewriting prompt, query-replace, keymode,
  pending-open-url, and input fields.
- Added a focused regression that monkeypatches the editor aggregate owner
  methods, mutates delayed interaction state, and proves failed callback rollback
  routes through the owner while restoring the previous state.
- Extended `tools/mxaudit.py --check` and human output with
  `plugin_callback_interaction_owner_present=True` /
  `callback-interaction-owner=True`.

## Audit/refactor value

This is intentionally not a new registry. It retires a live compatibility seam
that rev0935 explicitly named as remaining risk. Runtime rollback still decides
when broad callback rollback is needed, but the editor now owns how delayed
interaction rows are captured and restored.

The refactor also makes the next interaction-family addition harder to get
wrong: a new delayed interaction must be included in the editor aggregate owner,
not copied into plugin runtime as another raw field.

## Validation

Run from the repository root:

```sh
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  pytest -q tests/test_plugin_callback_scoped_snapshot.py tests/test_mxaudit.py

PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  pytest -q \
  tests/test_plugin_runtime_group_policy.py::test_runtime_group_interaction_snapshot_restore_uses_keymode_owner \
  tests/test_plugin_runtime_group_policy.py::test_runtime_generation_interaction_snapshot_restore_uses_keymode_owner

PYTHONPATH=src python tools/mxaudit.py --check --limit 3
PYTHONPATH=src python tools/mxcontext.py --check
PYTHONPATH=src python tools/mxlint.py
```

Observed in the rev0936 cloudtainer before packaging:

- `tests/test_plugin_callback_scoped_snapshot.py tests/test_mxaudit.py`: `6 passed`
- focused active-interaction owner selectors plus audit while editing: `7 passed`
- selected plugin-runtime/callback authority suite (`tests/test_plugin_runtime_group_policy.py` plus clipboard/message/palette/recent/search callback rollback tests): `95 passed, 19 warnings`
- `tools/mxaudit.py --check`: clean check with
  `callback-interaction-owner=True`
- `tools/mxcontext.py --check`: clean context for rev0936
- `tools/mxlint.py`: `mxlint: ok`

## Remaining risk

- Broad `RuntimeRegistrationSnapshot` still has 40 fields and remains the
  source/lifecycle/deinit fallback where overwrites need full restoration.
- `snapshot_runtime_registrations()` still owns several non-interaction state
  families directly. Move only those with concrete stale/lifetime or authority
  bugs, not because a table says every field needs a wrapper.
- Editor-side `remove_interaction_group()` and
  `remove_plugin_interaction_generation()` still coordinate multiple delayed
  interaction families internally. That is acceptable because ownership is
  inside the editor, but a future pass can split helpers if it removes a
  concrete double-clear or retention bug.
- This remains an in-process application boundary, not OS sandboxing, memory
  isolation, native-code containment, or protection from malicious plugins.

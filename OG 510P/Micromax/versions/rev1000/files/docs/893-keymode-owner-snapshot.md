# Keymode owner snapshot (rev0935)

Rev0935 closes the next active-interaction ownership seam after pending
open-url, query-replace, and prompt: active keymodes. Keymodes are not just UI
labels. A plugin or script can push a capture mode, return to the host, and let
a later physical key decide which binding receives authority. Runtime cleanup and
rollback therefore should not read or rewrite `Editor.key_mode_stack` directly.

## External check

The online check stayed narrow and implementation-bound:

- OWASP API4:2023, Unrestricted Resource Consumption:
  <https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/>
- MITRE CWE-400, Uncontrolled Resource Consumption:
  <https://cwe.mitre.org/data/definitions/400.html>
- MITRE CWE-772, Missing Release of Resource after Effective Lifetime:
  <https://cwe.mitre.org/data/definitions/772.html>

The Micromax rule remains concrete: delayed interaction resources need one owner
for capture, pruning, and restore over their effective lifetime. For keymodes,
that owner is the editor, because the stack order, capture flag, once flag,
script origin, plugin generation, and runtime group all decide who receives a
future keypress.

## What changed

- Added `KeyModeInteractionRow` and `KeyModeInteractionSnapshot` in `editor.py`
  as the editor-owned value objects for active keymode delayed-authority rows.
- Added keymode owner methods for group and generation snapshot/restore:
  `snapshot_key_mode_group_state()`, `restore_key_mode_group_state()`,
  `snapshot_key_mode_generation_state()`, and
  `restore_key_mode_generation_state()`.
- Refactored `plugin_runtime.py` group/generation interaction snapshot and
  restore to call those owner methods instead of enumerating or rewriting
  `Editor.key_mode_stack` directly.
- Preserved existing runtime snapshot shape by storing the editor-owned row
  payload in the existing `key_modes` field.
- Added focused regressions that monkeypatch the keymode owner methods and prove
  runtime group/generation snapshot+restore routes through them.
- Extended `tools/mxaudit.py --check` with
  `keymode_owner_snapshot_present=True` and human output `keymode-owner=True`.

## Audit/refactor value

This is a refactor of a live rollback path, not a new registry. The runtime
transaction wrapper still coordinates plugin unload/reload cleanup, but the
editor now owns all four active delayed-interaction families that can outlive a
callback and later receive authority: keymode, prompt, query-replace, and
pending open-url.

The value is not that keymodes became safer by name alone. The value is that the
code that understands keymode stack semantics now owns group/generation pruning
and reinsertion order, while `plugin_runtime.py` only asks for the relevant
snapshot/restore operation.

## Validation

Run from the repository root:

```sh
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  pytest -q \
  tests/test_plugin_runtime_group_policy.py::test_runtime_group_interaction_snapshot_restore_uses_keymode_owner \
  tests/test_plugin_runtime_group_policy.py::test_runtime_generation_interaction_snapshot_restore_uses_keymode_owner

PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  pytest -q tests/test_plugin_runtime_group_policy.py tests/test_mxaudit.py

PYTHONPATH=src python tools/mxaudit.py --check --limit 3
PYTHONPATH=src python tools/mxcontext.py --check
PYTHONPATH=src python tools/mxlint.py
```

Observed in the rev0935 cloudtainer before packaging:

- focused keymode-owner selector: `2 passed`
- `tests/test_plugin_runtime_group_policy.py tests/test_mxaudit.py`: `47 passed, 13 warnings`
- `tests/test_revision_index.py tests/test_docs_living_hygiene.py tests/test_mxcontext.py`: `9 passed`
- `tools/mxaudit.py --check --limit 3`: clean check with `keymode-owner=True`
- `tools/mxcontext.py --check`: clean context check for rev0935
- `tools/mxlint.py`: `mxlint: ok`

## Remaining risk

- Broad failed-callback interaction snapshots still store prompt/qreplace/open-url
  and keymode state directly for compatibility. That can become a later single
  full-interaction owner helper if it stays small and does not widen rollback
  semantics.
- `remove_interaction_group()` and `remove_plugin_interaction_generation()` still
  coordinate multiple active-interaction cleanup families in the editor. That is
  acceptable for now because ownership is already inside the editor, but a future
  pass can split internal helpers if it reduces coupling.
- This remains an in-process application boundary, not hostile-code containment,
  memory isolation, or an operating-system sandbox.

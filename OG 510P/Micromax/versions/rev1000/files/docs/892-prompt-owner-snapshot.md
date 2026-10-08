# Prompt owner snapshot (rev0934)

Rev0934 finishes the smallest active-interaction owner seam that rev0933 left
open: the live prompt row. Prompt is not just a UI string. A plugin or script can
open a prompt, return to the host, and leave a delayed authority object that
will later drive completion reads, picker navigation/copy, or command submit.
Runtime cleanup and rollback therefore should not edit `Editor.prompt` directly
from `plugin_runtime.py`.

## External check

The online check stayed deliberately narrow:

- MITRE CWE-400, Uncontrolled Resource Consumption:
  <https://cwe.mitre.org/data/definitions/400.html>
- MITRE CWE-772, Missing Release of Resource after Effective Lifetime:
  <https://cwe.mitre.org/data/definitions/772.html>
- OWASP API4:2023, Unrestricted Resource Consumption:
  <https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/>

For Micromax, the practical rule is not a new registry. Delayed interaction rows
should have one owner that controls capture, clear, and restore over their
effective lifetime. Prompt rows are resource and authority surfaces because they
can outlive the callback that created them and can later cause reads, command
execution, or picker actions.

## What changed

- Added `PromptInteractionSnapshot` in `editor.py` as the editor-owned value
  object for the active prompt delayed interaction row.
- Added prompt owner methods for group and generation snapshot/restore:
  `snapshot_prompt_group_state()`, `restore_prompt_group_state()`,
  `snapshot_prompt_generation_state()`, and
  `restore_prompt_generation_state()`.
- Added `_clear_prompt_runtime_row()` and `_restore_prompt_snapshot()` so prompt
  cleanup and restore semantics live beside the prompt authority model.
- Refactored `plugin_runtime.py` group/generation interaction snapshot and
  restore to call prompt owner methods instead of reading or writing
  `Editor.prompt` directly.
- Kept the existing runtime snapshot shape compatible by storing the owner
  payload in the existing `prompt` / `prompt_captured` fields.
- Added focused regressions that monkeypatch the prompt owner methods and prove
  runtime group/generation snapshot+restore routes through them.
- Extended `tools/mxaudit.py --check` with
  `prompt_owner_snapshot_present=True` and human output `prompt-owner=True`.

## Audit/refactor value

This is intentionally a runtime refactor, not more doctrine. The transaction
wrapper in `plugin_runtime.py` still coordinates cleanup and rollback, but the
editor now owns the active prompt row in the same style as rev0932's pending
open-url owner and rev0933's query-replace owner. The hot runtime path no longer
needs to know how prompt group/generation ownership is represented.

The remaining direct field access in broad failed-callback snapshots is now a
separate compatibility path. Runtime group/generation cleanup, unload/reload
rollback, and generation restore use typed prompt owner methods.

## Validation

Run from the repository root:

```sh
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  pytest -q \
  tests/test_plugin_runtime_group_policy.py::test_runtime_group_interaction_snapshot_restore_uses_prompt_owner \
  tests/test_plugin_runtime_group_policy.py::test_runtime_generation_interaction_snapshot_restore_uses_prompt_owner \
  tests/test_plugin_runtime_group_policy.py::test_runtime_group_snapshot_captures_only_touched_interaction_rows \
  tests/test_plugin_runtime_group_policy.py::test_runtime_generation_snapshot_scopes_interaction_rows

PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  pytest -q tests/test_plugin_runtime_group_policy.py tests/test_mxaudit.py

PYTHONPATH=src python tools/mxaudit.py --check --limit 3
PYTHONPATH=src python tools/mxcontext.py --check
PYTHONPATH=src python tools/mxlint.py
```

Observed in the rev0934 cloudtainer before packaging:

- focused prompt-owner selector: `4 passed`
- `tests/test_plugin_runtime_group_policy.py tests/test_mxaudit.py`: `45 passed, 13 warnings`
- `tests/test_revision_index.py tests/test_docs_living_hygiene.py tests/test_mxcontext.py`: `9 passed`
- `tools/mxcontext.py --check`: clean context check for rev0934
- `tools/mxlint.py`: `mxlint: ok`
- `tools/mxaudit.py --check --limit 3`: clean check with `prompt-owner=True`

## Remaining risk

- Broad failed-callback interaction snapshots still store prompt/qreplace/open-url
  state directly for compatibility; a later slice can route that broad fallback
  through editor-owned full interaction snapshot helpers if it stays small.
- Active keymode stack ownership is still partly runtime-shaped. It has group and
  generation helpers, but not the same editor-owned value object pattern as
  prompt/open-url/query-replace.
- This remains an in-process application boundary, not hostile-code containment,
  memory isolation, or an operating-system sandbox.

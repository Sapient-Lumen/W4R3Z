# Clipboard owner snapshot (rev0937)

Rev0937 moves the internal clipboard singleton behind editor-owned snapshot and
restore methods for group cleanup, generation cleanup, and the broad
registration fallback. Rev0883 originally made clipboard cleanup a touched
singleton snapshot. That was a useful rollback boundary, but by rev0936 it still
left `plugin_runtime.py` reading and rewriting `Editor.clipboard_items`,
`clipboard_kind`, `clipboard_authority`, `clipboard_serial`, and
`clipboard_from_script` in the primary rollback path.

That is a concrete lifetime risk: the internal clipboard is not just a list of
strings. It is delayed paste/export state with authority provenance and serial
semantics. If runtime glue restores some fields but misses one owner-side side
effect, a plugin-owned clipboard can leak past unload, or a trusted/user
clipboard can be cleared during a failed plugin cleanup.

## External check

The online check stayed implementation-bound:

- MITRE CWE-772, Missing Release of Resource after Effective Lifetime:
  <https://cwe.mitre.org/data/definitions/772.html>
- MITRE CWE-400, Uncontrolled Resource Consumption:
  <https://cwe.mitre.org/data/definitions/400.html>
- OWASP API4:2023, Unrestricted Resource Consumption:
  <https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/>

The applied rule is narrow: an owned delayed resource should have one place that
knows how to capture, clear, and restore its payload plus authority sidecars over
its effective lifetime. For the internal clipboard, that owner is now `Editor`,
not plugin-runtime broad snapshot glue.

## What changed

- Added `ClipboardRegisterSnapshot` in `editor.py` as the typed editor-owned
  snapshot for the internal clipboard register.
- Added `Editor.snapshot_clipboard_group_state()` and
  `Editor.restore_clipboard_group_state()` for group cleanup/retag rollback.
- Added `Editor.snapshot_clipboard_generation_state()` and
  `Editor.restore_clipboard_generation_state()` for plugin generation cleanup.
- Refactored `plugin_runtime.snapshot_clipboard_group_state()` /
  `restore_clipboard_group_state()` and their generation variants to ask the
  editor owner methods first, while preserving fallback behavior for alternate
  embedders.
- Refactored `snapshot_runtime_registrations()` so the broad lifecycle/source
  fallback captures the clipboard through `snapshot_clipboard_group_state(ed,
  groups=None)` instead of direct raw field reads.
- Refactored `restore_runtime_registrations()` so broad fallback restores the
  clipboard through `restore_clipboard_group_state()` before the legacy raw-field
  compatibility path.
- Fixed a scoped-generation regression discovered by the new test: a scoped
  generation restore must not let the legacy broad raw-field block clobber a
  just-restored clipboard authority with `None`.
- Added focused regressions for group, generation, and broad registration
  snapshot/restore routes by monkeypatching the editor owner methods.
- Extended `tools/mxaudit.py --check` and human output with
  `clipboard_owner_snapshot_present=True` / `clipboard-owner=True`.

## Audit/refactor value

This is intentionally not a new registry. It retires one real raw-state coupling
that remained after the broader callback-interaction owner slice. The runtime
still decides when group, generation, or broad lifecycle rollback is needed; the
editor now decides how the clipboard singleton is represented, cleared, and
restored.

The same pattern also reduced accidental waste: while validating the owner route,
the focused generation test caught an old broad restore footgun that could erase
a scoped clipboard authority after the scoped owner had restored it. That bug is
small, but it is exactly the kind of cross-path state clobber that owner methods
are meant to prevent over time.

## Validation

Run from the repository root:

```sh
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  pytest -q \
  tests/test_plugin_runtime_group_policy.py::test_runtime_group_clipboard_snapshot_restore_uses_editor_owner \
  tests/test_plugin_runtime_group_policy.py::test_broad_registration_clipboard_snapshot_restore_uses_editor_owner \
  tests/test_plugin_runtime_group_policy.py::test_runtime_generation_clipboard_snapshot_restore_uses_editor_owner \
  tests/test_mxaudit.py::test_mxaudit_json_reports_repeatable_structural_signals

PYTHONPATH=src python tools/mxaudit.py --check --limit 3
PYTHONPATH=src python tools/mxcontext.py --check
PYTHONPATH=src python tools/mxlint.py
```

Observed in the rev0937 cloudtainer before packaging:

- focused clipboard owner selectors plus audit JSON selector: `4 passed`
- broader plugin-runtime group policy plus audit selector: `50 passed, 13 warnings`
- `tools/mxaudit.py --check`: clean check with `clipboard-owner=True`
- `tools/mxcontext.py --check`: clean context for rev0937
- `tools/mxlint.py`: `mxlint: ok`

## Remaining risk

- Broad `RuntimeRegistrationSnapshot` still owns several non-interaction fields
  directly. Move only the next one with a concrete stale/lifetime or authority
  failure, not by wrapper quota.
- Active search is still a good candidate because it is another singleton with
  authority sidecars and broad/generation paths, but it should be moved only if a
  focused route test can prove reduced raw-state coupling.
- Prompt history, saved cursors, recent files, and palette MRU still have mixed
  owner/fallback seams; their row-shaped data is less risky than the active
  singleton interactions unless a stale-authority bug is found.
- This remains an in-process application boundary, not OS sandboxing, memory
  isolation, native-code containment, or protection from malicious plugins.

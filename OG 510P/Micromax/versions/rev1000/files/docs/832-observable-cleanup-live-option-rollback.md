# Rev0874 — observable cleanup and live-buffer option rollback

Date: 2026-06-18

Rev0874 is a small runtime-risk landing. It intentionally avoids a new effect
registry or broad plugin contract. Instead it fixes two concrete weaknesses from
the rev0873 audit and improves one release-confidence check.

## What changed

### Runtime group cleanup is now inspectable

`plugin_runtime.cleanup_runtime_group()` and `retag_runtime_group()` used to run
a long sequence of `try/except Exception: pass` calls. That preserved best-effort
cleanup, but it also meant a broken cleanup method could leave plugin-owned state
behind with no structured evidence.

They now return `RuntimeGroupOperationReport` rows. Each attempted surface records
its action, status, changed count when available, and failure detail. The sweeps
still continue after a failure so one broken surface does not suppress later
cleanup, but tests and future policy can now see whether cleanup was actually
clean.

`PluginManager` keeps a bounded `runtime_group_reports` trail and exposes
`runtime_group_failures()` so unload/reload paths have session-local evidence
without changing the user-facing command dialect yet.

This is not yet fail-fast cleanup. It is the observable seam needed before a safe
fail-fast policy can be introduced.

### Buffer-local option rollback follows live buffer identity

Rev0872 restored buffer-local options by buffer name. That was a narrow but real
risk because buffer names can change and old names can be reused. A failed plugin
transaction should restore the live buffer objects that existed when the snapshot
was taken, not a later replacement buffer that happens to share a name.

`OptionStateSnapshot` now carries `BufferLocalOptionSnapshot` rows bound to the
actual `EditorBuffer` object. Restore prefers those identity-bound rows. The old
by-name map remains as readable/debug fallback for older snapshots, but new
snapshots do not apply stale local options to replacement buffers.

### Typecheck coverage includes the editor package

`scripts/typecheck.sh` now targets `src/micromax_editor` and `tools` in addition
to the VM and tests. This does not solve the offline skip behavior when mypy is
not installed, but it removes the much larger omission identified by rev0873's
audit metrics.

## What did not change

- No new sandbox, process isolation, or hostile-code containment is claimed.
- Runtime group cleanup still does not raise automatically on partial failure.
- Option rollback is still limited to option values; document edits, opens,
  saves, shell/URL effects, and external clipboard exports remain outside this
  rollback boundary unless a narrower contract says otherwise.
- `RuntimeRegistrationSnapshot` still has 40 fields. The goal of this revision
  was to harden two risky seams before starting a larger journal extraction.

## Evidence

Focused verification for this landing:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  python -m pytest -q \
  tests/test_editor_plugin_option_rollback.py \
  tests/test_plugin_runtime_group_reports.py \
  tests/test_plugin_reload_recovery.py \
  tests/test_mxaudit.py
```

Additional handoff checks should include:

```bash
python tools/mxlint.py
python tools/mxcontext.py --check
make audit-metrics
```

A fresh full aggregate manifest is still pending before any release-wide claim.

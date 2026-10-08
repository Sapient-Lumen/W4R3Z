# Rev0875 — runtime cleanup commit guards

Date: 2026-06-18

Rev0875 turns the rev0874 cleanup evidence seam into commit policy for the most
misleading plugin transitions. The goal is deliberately narrow: when unload or
reload cannot clean or promote every required runtime-group surface, Micromax no
longer reports a clean unload/reload while leaving mixed plugin state behind.

## What changed

### Partial cleanup is no longer a clean unload

`PluginManager.unload()` now treats runtime-group cleanup as a commit-critical
operation. It snapshots dictionary and runtime-registration state immediately
before the cleanup sweep. If any surface in the `RuntimeGroupOperationReport`
fails, Micromax restores the pre-sweep state, keeps the plugin in the loaded
plugin table, records a load/error diagnostic, and raises
`RuntimeGroupOperationError`.

This is not a sandbox. It is a truthfulness guard: a plugin should not disappear
from the manager while commands, hooks, timers, history, search, clipboard, or
other delayed state may still be live.

### Failed reload cleanup or retag restores the old plugin

Staged reload has two commit-critical sweeps:

1. cleanup of the old committed runtime group;
2. retagging of the staged replacement group to the stable plugin group.

Both now run under a pre-operation snapshot. If either sweep reports a failed
surface, the staged group is removed best-effort, the full pre-reload snapshot is
restored, the old plugin remains the advertised loaded generation, and the
failure report is retained for inspection.

The important behavior is not merely raising. The important behavior is avoiding
a false mixed state such as “new plugin is loaded” while some staged rows remain
under `#reload` or some old rows survived cleanup.

### Reports now have a policy error type

`RuntimeGroupOperationError` carries the original
`RuntimeGroupOperationReport`. Callers can inspect the exact failed surface,
action, and detail while user-facing messages stay concise.

`PluginManager.runtime_group_reports` still retains bounded session-local
operation evidence, so a failed unload/reload can be diagnosed after the fact.

### Audit now checks the commit guards

`tools/mxaudit.py` now reports runtime-group policy signals:

- operation-error class present;
- manager retains cleanup/retag reports;
- unload uses a cleanup commit guard;
- reload uses cleanup and retag commit guards.

`mxaudit --check` treats those as audit-integrity checks, not structural-debt
warnings. This keeps the new policy from quietly regressing back into
best-effort-only cleanup.

## What did not change

- Cleanup during already-failing source/lifecycle evaluation still preserves the
  original plugin error and records cleanup failures through retained reports;
  this revision does not make those cleanup reports mask the primary failure.
- `force=True` skips lifecycle/dependent checks, but it does not allow Micromax
  to claim a clean removal if the required runtime-group cleanup sweep fails.
- Broad rollback still covers only the enumerated runtime-registration and
  delayed-state surfaces in `RuntimeRegistrationSnapshot`.
- Document edits, new buffers, opens, saves, shell/URL effects, external
  clipboard exports, blocking calls, memory exhaustion, native code, and process
  compromise are still outside this rollback guarantee.
- The 40-field snapshot remains; this revision adds commit guards before any
  typed journal extraction.

## Evidence

Focused verification for this landing:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  python -m pytest -q \
  tests/test_plugin_runtime_group_policy.py \
  tests/test_plugin_runtime_group_reports.py \
  tests/test_plugin_reload_recovery.py \
  tests/test_editor_plugin_option_rollback.py \
  tests/test_mxaudit.py
```

Additional handoff checks:

```bash
python tools/mxlint.py
python tools/mxcontext.py --check
python tools/mxaudit.py --check
```

A fresh complete aggregate manifest is still pending before any release-wide
claim.

# Rev0861 — revoked grants withhold callbacks and plugin unload recovers runtime

## Why this revision exists

Rev0860 made restricted plugin callback lazy-includes content-bound: if package
bytes changed after load, old callbacks lost package-local `include` / `require`
authority until a fresh approved reload landed.  One practical recovery seam was
still too loose:

- revoking a restricted load grant blocked reloads, but unchanged loaded callbacks
  could still lazy-load package files because the package digest still matched;
- users had no command-bar way to unload an already-loaded plugin without
  restarting, even though the plugin manager already had a transactional unload
  path.

That made revocation less meaningful than it looked.  It was a future-load guard,
not a way to stop future package-local source reads from a loaded generation.

## Runtime behavior

Restricted callback package-local source loading now requires both conditions:

1. the loaded plugin generation's package digest still matches disk; and
2. the session load grant for that plugin is still active and matches the loaded
   digest.

If the grant is revoked, callbacks may still run as lower-authority plugin code,
but package-local `include` / `require` is withheld.  Without a separate
`cap.fs-require` grant, attempted helper loads fail closed.

A new interactive command closes the adjacent recovery gap:

```text
plugin unload NAME
```

`plugin unload NAME` removes one loaded plugin through the existing plugin-manager
cleanup transaction.  In restricted mode it also revokes the matching session load
grant, so loading that plugin again remains an explicit `plugin load NAME`
decision.  Script contexts cannot run `plugin unload NAME`.

## Audit/refactor performed

The refactor stayed deliberately small:

- `PluginManager._loaded_plugin_record()` centralizes loaded-plugin lookup for
  package checks.
- `PluginManager.loaded_plugin_package_authorized()` composes package freshness
  with grant liveness instead of making `Editor` inspect grant internals.
- `Editor.plugin_callback_context()` asks that one manager method before restoring
  package-local load roots in restricted mode.
- `Editor.plugin_unload_with_feedback()` exposes the existing transactional
  unload path with the same concise command feedback style as `plugin load` /
  `plugin reload`.

No durable permission store, broad registry, or process-isolation claim was added.

## Boundary and residual risk

Revocation is still not process isolation.  Already evaluated plugin words and
already registered commands can run until the user unloads the plugin, and a
malicious loaded plugin still runs in the same Python process.  This revision
only closes two application-level recovery gaps: revoked grants no longer allow
future package-local helper loads, and users can remove a loaded plugin surface
without restarting.

## Evidence

Focused validation added and passed:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  pytest -q tests/test_editor_plugin_manual_load_grants.py tests/test_plugin_containment_and_caps.py
```

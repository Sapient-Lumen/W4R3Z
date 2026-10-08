# Rev0860 — callback-time package include guard

## Why this revision exists

Rev0859 made restricted plugin grants content-bound for `plugin load NAME` and
`plugin reload NAME`.  That closed the obvious stale-reload path, but one
higher-risk seam remained: already-loaded plugin callbacks can run later and
lazy-load package-local helpers with `include` or `require`.

Without an additional check, a user could approve and load a plugin, then a
helper file could change on disk, and a command/key/timer/hook callback could
load the changed helper without a successful restricted reload.  That would make
content-bound approval true at load time but false at callback time.

## Runtime behavior

Restricted workspaces now give plugin callbacks package-local source-load
authority only while the loaded plugin generation still matches its committed
package digest.

- Successful restricted plugin loads store the loaded package digest on the
  `Plugin` generation, not only on the session grant.
- Restricted plugin reloads carry the new package digest onto the reloaded
  generation.
- When a deferred plugin callback fires, Micromax rechecks the current package
  digest before restoring the callback's package-local include root.
- If the package changed, the callback still runs as lower-authority plugin
  script code, but package-local `include` / `require` is withheld.  Without a
  separate `cap.fs-require` grant, the attempted load fails closed.
- Running `plugin load NAME` on an already loaded plugin re-approves bytes for a
  future reload; it does not silently let old callbacks load changed helper
  files.  The user must run `plugin reload NAME` under the fresh grant.

Trusted-mode plugin callbacks keep their existing behavior.

## Audit/refactor performed

The refactor is intentionally narrow:

- `Plugin` now records `package_digest` and `package_file_count` for the loaded
  generation when a content-bound grant was used.
- `PluginManager.loaded_plugin_package_current()` centralizes the freshness
  check used by callback authority.
- `Editor.plugin_callback_context()` now asks the plugin manager whether the
  loaded generation is still current before restoring package-local load roots in
  restricted mode.

No durable permission database, registry, or broad extension API change was
added.

## Boundary and residual risk

This guard controls later package-local source loading.  It does not stop already
loaded words from executing, and it does not make plugin code safe.  The system
still runs inside one Python process, and the digest check remains a best-effort
application-level stale-byte check rather than atomic filesystem attestation.

The defended case is narrower and concrete: a changed helper file should not be
lazy-loaded by an old restricted callback until the user explicitly reloads the
plugin under a fresh content-bound approval.

## Evidence

Focused validation added and passed:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  pytest -q tests/test_editor_plugin_manual_load_grants.py tests/test_plugin_containment_and_caps.py
```

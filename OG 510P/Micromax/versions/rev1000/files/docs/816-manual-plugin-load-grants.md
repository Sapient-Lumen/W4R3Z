# Rev0858 — restricted manual plugin-load grants

## Why this revision exists

Rev0857 stopped automatic plugin and user-init evaluation in restricted
workspaces, but one recovery path still made the boundary ambiguous:
`plugin reload NAME` could load a scanned, available plugin because reload had a
longstanding trusted-mode repair behavior for unloaded candidates.

Rev0858 keeps the repair behavior in trusted workspaces and makes restricted
workspaces explicit: scanning is still no-exec, reload is only for already loaded
plugins, and a user deliberately runs `plugin load NAME` before one plugin source
is evaluated.

## Runtime behavior

- `plugin reload NAME` no longer loads an available-but-unloaded candidate in
  restricted mode. It tells the user to run `plugin load NAME` instead.
- `plugin load NAME` creates a session grant bound to the plugin name, root,
  current entry file, and in rev0859 the package digest, then loads the candidate.
- `plugin load NAME` on an already loaded plugin in restricted mode refreshes the
  candidate metadata and records a new session grant for future reload approval.
- `plugin reload NAME` in restricted mode requires a non-revoked grant that still
  matches the current on-disk candidate.
- `plugin grants` lists session grants.
- `plugin revoke NAME` marks one grant revoked.
- Trusted mode keeps the previous recovery semantics; `plugin load NAME` is a
  clearer explicit alias for loading a known available candidate.

## Audit/refactor performed

The grant record is deliberately small and executable rather than a large policy
registry:

- `PluginLoadGrant` stores plugin, root, entry, issuer, duration, provenance,
  issue order, revocation state, and use count.
- `PluginManager.refresh_candidate()` centralizes re-reading plugin metadata and
  entry containment before grant-sensitive decisions.
- `PluginManager.load_available()` accepts an optional grant and refuses stale
  approvals.
- Restricted reload rechecks disk before trusting an existing grant, so a changed
  `plugin.json`, entry path, or same-path package byte cannot reuse an older approval.
- Prompt completion and plugin command summaries were updated to expose `load`,
  `grants`, and `revoke` without inventing a broad new registry.

## Script boundary

Restricted-mode manual approval is treated as a user decision, not something a
script can grant to itself:

- scripts cannot run `plugin load NAME` in restricted mode, even with
  `cap.fs-require`;
- scripts cannot run `plugin revoke NAME`;
- scripts cannot see `plugin grants` without `cap.plugin-read`.

This is still application policy inside the Python process. It does not make
plugin source safe; it only removes silent automatic and hidden recovery loads.

## Non-guarantees

The grant is session-local and in memory. Rev0859 binds it to a package digest, but that remains a stale-grant check rather than signed provenance. It is not a signed provenance record,
not a per-plugin permission store, not process isolation, and not a hostile-code
sandbox. A user who explicitly loads a malicious plugin is still running that
plugin inside the same Python process.

## Evidence

Focused validation added and passed:

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  pytest -q tests/test_editor_plugin_manual_load_grants.py
```

The test file covers no hidden restricted reload, explicit load grants, revoked
grants, stale grant detection after on-disk entry changes, script denial for
restricted load/revoke, grant-list visibility gating, and trusted-mode recovery
compatibility.


## Rev0859 addendum

`PluginLoadGrant` now stores `package_digest` and `package_file_count`. See `docs/817-content-bound-plugin-grants.md` for the content-bound stale-grant boundary.

# Rev0859 — content-bound restricted plugin grants

## Why this revision exists

Rev0858 made restricted plugin loading explicit, but the grant still named the
plugin root and entry path rather than the bytes that would later execute.  That
left a stale-approval gap: a user could approve `plugin load NAME`, then the same
`init.mx` or an included helper could change on disk before `plugin reload NAME`.
The path would still match even though the reviewed source no longer did.

Rev0859 closes that gap for the in-process trust boundary.  A restricted plugin
load grant is now content-bound to a digest of the current plugin package files.
Changing the entry file, `plugin.json`, an included `.mx` helper, or any other
ordinary file in the plugin directory makes the old grant stale until the user
explicitly runs `plugin load NAME` again.

## Runtime behavior

- `plugin load NAME` in restricted mode records the current package digest and
  file count on the session grant before source evaluation.
- `plugin reload NAME` in restricted mode re-reads candidate metadata and
  recomputes the package digest before accepting an existing grant.
- Same-path content edits now invalidate a grant just like a `plugin.json` entry
  change did in rev0858.
- `plugin load NAME` on an already loaded plugin remains the explicit
  re-approval step; the following `plugin reload NAME` can then evaluate the
  newly approved bytes.
- Trusted-mode loading and reload recovery remain unchanged.

## Audit/refactor performed

The change stays small:

- `PluginLoadGrant` gained `package_digest` and `package_file_count` fields.
- `PluginManager` gained a private package-fingerprint seam used by grant
  creation and matching.
- `plugin_io.read_plugin_bytes()` centralizes contained byte reads so metadata,
  source evaluation, and fingerprinting use the same fd-backed containment
  boundary.

The implementation deliberately avoids a durable permission database or broad
policy registry.  It is still one session-local approval record with stronger
staleness semantics.

## Boundaries and residual risk

This is not a sandbox.  A re-approved plugin still runs inside the same Python
process.  The digest is an application-level stale-grant check, not signed supply
chain provenance or atomic file-system attestation. Rev0860 extends the same
content-bound idea to callback-time lazy includes, but already loaded words still
execute inside the same process.

The fingerprint covers ordinary files under the plugin directory because plugin
source may `include` or `require` package-local helpers.  That is intentionally
conservative: changing data files under the plugin root can also require
re-approval in restricted mode.  The safer default is to stale a grant too often
rather than to reuse approval for bytes the user did not approve.

## Evidence

Focused validation added and passed:

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  pytest -q tests/test_editor_plugin_manual_load_grants.py
```

The expanded focused plugin/trust lane also passed after this change, including
plugin containment, load-error, reload-recovery, prompt-completion, workspace
trust, and command-surface tests.

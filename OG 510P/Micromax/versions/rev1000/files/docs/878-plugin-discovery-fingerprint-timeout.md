# Rev878 / rev0920 — plugin discovery and package fingerprint timeout

## Why this pass

Rev0919 left the most security-sensitive discovery seam untouched: plugin roots.
Restricted workspaces correctly avoided automatic plugin execution, and manual
plugin load grants were bound to package bytes, but the act of discovering
plugins and computing those grant fingerprints still used ordinary top-level and
recursive filesystem walking.  That is risky in exactly the wrong place: before
plugin code is approved, a large, remote, or wedged plugin tree could consume the
session.

The online check kept the choice concrete.  Python subprocess/process timeouts
provide a kill/wait cleanup boundary for blocking work, while thread-pool
cancellation cannot reliably stop already-running blocking I/O.  OWASP API4
continues to classify missing execution and resource limits as resource
consumption risk.  The fix therefore moves plugin discovery/fingerprint I/O onto
bounded filesystem seams instead of adding another policy registry.

Research references:

- https://docs.python.org/3/library/subprocess.html
- https://docs.python.org/3/library/concurrent.futures.html
- https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- https://discuss.python.org/t/graceful-exit-from-threadpoolexecutor-when-blocked-on-io-problem-and-possible-enhancement/80380

## What changed

`src/micromax_editor/plugins.py` now gives plugin discovery and grant
fingerprinting explicit budgets:

- `PLUGIN_DISCOVERY_MAX_DIRS`
- `PLUGIN_DISCOVERY_TIMEOUT_SECONDS`
- `PLUGIN_PACKAGE_FINGERPRINT_TIMEOUT_SECONDS`
- per-manager `plugin_discovery_max_dirs`, `plugin_discovery_timeout_seconds`,
  and `package_fingerprint_timeout_seconds`

Top-level plugin discovery now calls `list_dir_contained_bounded()` with the
plugin root as the containment root and a positive row cap.  Missing or
non-directory roots still behave as “no plugins,” but the previous
`rootp.iterdir()` traversal is retired.  Symlinked plugin directories are still
allowed only when a bounded contained stat follow proves the target remains
inside the configured plugin root; escaping symlinks remain visible as load
errors.

Manual-load package fingerprinting now runs the recursive package scan and
contained byte reads in one killable worker.  The old file-count and total-byte
budgets are preserved, but now a stuck recursive walk or file read can fail
closed with `plugin fingerprint timed out after ...` instead of monopolizing the
editor.  The direct in-process implementation remains only for explicit
`package_fingerprint_timeout_seconds <= 0` debug/test embeddings.

`tools/mxaudit.py` adds `plugin_discovery_fingerprint_timeout_boundary`, tying
the code to regressions that assert bounded discovery and fingerprint timeout
behavior.  This is intentionally not a generated effect table yet; it fixes the
remaining plugin-root survivor first.

## Validation

Focused validation passed:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_plugin_package_fingerprint_budgets.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_plugin_containment_and_caps.py tests/test_plugin_json_schema.py tests/test_editor_workspace_trust.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_editor_plugin_manual_load_grants.py tests/test_plugin_load_errors.py tests/test_editor_pluginpick.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_editor_plugin_authority.py tests/test_plugin_reload_recovery.py tests/test_plugin_retired_wordlists.py tests/test_plugin_runtime_group_policy.py tests/test_plugin_runtime_group_reports.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_editor_prompt_completion_hostcalls.py -k 'plugin'
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q tests/test_mxcontext.py tests/test_mxaudit.py tests/test_revision_index.py tests/test_docs_living_hygiene.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxlint.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxcontext.py --check
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxaudit.py --json --check --limit 1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxportable.py --json
```

The plugin-focused lanes, living-doc/audit/context checks, lint, and portable
matrix passed.  They emit the same POSIX fork deprecation warning family already
present in earlier filesystem timeout tests because the worker context
deliberately prefers `fork` on POSIX to preserve in-process test doubles and
avoid spawn import surprises.  A broader selected pytest lane and `make timely`
were attempted separately but hit the cloudtainer outer timeout/termination, so
this is not a full release-suite claim.

## Remaining risk

Plugin discovery is now bounded at the top-level root and package fingerprint
work is killable, but docs-root and project-root discovery helpers still deserve
a narrow sweep before generating a filesystem effect table.  The next useful
pass should retire one more concrete ambient discovery path or compact repeated
docs/evidence overhead; it should not start with a registry.

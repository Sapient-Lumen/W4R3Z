# Rev0857 — workspace trust and restricted startup

## Why this revision exists

Rev0856 named the missing runtime boundary: users should be able to inspect an
unfamiliar workspace without Micromax automatically evaluating workspace or user
configuration code. Rev0857 turns that from doctrine into executable startup
behavior.

The change is intentionally small. It does not claim hostile-code containment;
it blocks only automatic Micromax code loading during startup.

## Behavior

Startup now has two trust states:

- `trusted` is the compatibility default. It loads plugins and the user init file
  as previous revisions did.
- `restricted` scans plugin metadata and entry-file containment, but does not
  evaluate plugin source and does not load the user init file.

The CLI exposes the state directly:

```bash
python -m micromax_editor --trust restricted path/to/file.txt
python -m micromax_editor --trust restricted --tui path/to/file.txt
```

`MICROMAX_WORKSPACE_TRUST=restricted` provides the same startup policy when the
CLI flag is not supplied.

## Runtime surface

The editor records the effective state in `Editor.workspace_trust` and exposes a
small hostcall/model:

```micromax
trust-state  ( -- model )
```

The returned model is schema-tagged as `micromax.workspace-trust.v1` and reports
whether automatic plugin and user-init loading were allowed. Rev0858 extends the
restricted story after startup: manual plugin evaluation now goes through
`plugin load NAME` and a session grant rather than hidden reload recovery.

## Refactor performed

`PluginManager.load_tree()` used to combine discovery, dependency planning, and
source evaluation in one path. Rev0857 splits the front half into:

- `_discover_candidates()` — metadata and contained entry-file discovery only;
- `_candidate_load_order()` — dependency planning and blocked-state recording;
- `scan_tree()` — public non-evaluating discovery for restricted startup;
- `load_tree()` — compatibility path that scans, plans, then evaluates.

That is the audit/refactor slice: one real runtime seam now exists where trust
policy can stop before code execution.

## Guarantees

- Restricted startup can show plugin candidates without loading them.
- Restricted startup does not evaluate `MICROMAX_INIT` / `~/.config/micromax/init.mx`.
- Trusted startup preserves previous plugin and user-init autoload behavior.
- The trust-state model is accessible from the VM hostcall surface.
- Plugin dependency/cycle diagnostics still come from the same discovery/planning
  code used by the trusted loader.

## Non-guarantees

Restricted startup is not an OS sandbox. It does not make later manual commands,
explicit `include`/`require`, shell execution, Python process compromise, native
blocking, or malicious installed code safe. It is a startup automatic-code
boundary, not hostile-code isolation.

## Evidence

Focused validation added and passed:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  pytest -q \
  tests/test_editor_workspace_trust.py \
  tests/test_plugin_containment_and_caps.py \
  tests/test_plugin_hostcalls.py \
  tests/test_editor_plugin_authority.py
```

The current focused lane ran 79 tests cleanly across trust/plugin behavior,
context/revision hygiene, hostcall registry coverage, and the main CLI. A small
packaging/resource smoke lane then ran 7 additional tests cleanly.

`python tools/mxlint.py`, `python tools/mxcontext.py --check`,
`python -m compileall -q src tests tools`, and a restricted-mode headless CLI
smoke also passed. The ordinary full pytest stream was clean through roughly one
third of the suite before the cloudtainer command timeout, so the handoff should
rely on focused coverage plus the bounded aggregate runner for any full-release
claim.

## Next risk-reducing cuts

1. Add a small `trust` command or status row only if the UI needs it; avoid
   turning trust into another registry.
2. Write the concrete threat model now that startup and manual-load stop points exist.
3. Attach stable/experimental/internal labels to the plugin and hostcall surfaces.
4. Split one hostcall capability family using the same criterion: a real runtime
   stop point, not a paper abstraction.

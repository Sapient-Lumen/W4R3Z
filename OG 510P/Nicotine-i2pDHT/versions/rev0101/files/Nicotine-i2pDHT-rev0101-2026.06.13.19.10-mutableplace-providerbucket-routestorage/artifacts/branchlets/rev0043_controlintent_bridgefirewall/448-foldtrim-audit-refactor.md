# Foldtrim audit/refactor

`foldtrim.py` adds a small current-revision fold for rev0043 while preserving rev0042 `controlplanefold` as predecessor history.

The cube has accumulated many fold modules because each revision made a risky seam visible.  rev0043 does not delete that history.  It trims the current path by pinning only the new control/firewall surfaces and delegating predecessor checks to the existing control-plane fold, fold map, fold registry, and surface ledger.

Audit path:

- `audit_controlplane_fold(..., revision="rev0042")` remains predecessor proof;
- `audit_fold_map(..., revision="rev0043")` tracks current and historical fold paths;
- `audit_fold_registry(..., revision="rev0043")` pins active docs/tests/modules;
- `audit_surface_ledger(..., entries_for_revision("rev0043"))` keeps active surface visibility boring.

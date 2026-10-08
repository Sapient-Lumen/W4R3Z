# Foldseal audit/refactor

The cube has many historical fold modules.  rev0028 introduced `foldspine.py` to pin the current path.  rev0029 adds `foldseal.py` rather than rewriting the predecessor.

`foldseal.py` checks:

- rev0029 modules, tests, and docs exist;
- `PUBLIC_SURFACE.json` points at the current revision;
- `HEAD_REGISTRY.json` names checkpoint, egress, dispatch, and foldseal heads;
- `docs/00-index.md` exposes the new path;
- `README.md` and `START_HERE.md` name rev0029;
- `surfaceledger.py` knows rev0029;
- rev0028 `foldspine.py` still passes.

This is audit hygiene, not protocol authority.

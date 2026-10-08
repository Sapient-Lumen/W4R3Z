# Surface index audit/refactor

The cube keeps old branchlets and duplicate numeric prefixes because wake-from-amnesia history matters.  That creates a navigation risk: current surfaces can become hard to find.

`surfaceindex.py` audits only current-revision visibility:

- `PUBLIC_SURFACE.json` revision and entry paths,
- `HEAD_REGISTRY.json` revision and head paths,
- `docs/00-index.md` mentions of current docs,
- active surface ledger health.

This is intentionally not a cleanup hammer.  It does not delete history.  It makes current navigation drift visible.

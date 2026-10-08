# Fold spine audit/refactor

The cube has many historical fold modules because earlier revisions intentionally preserved branchlets instead of deleting them. That is good for wake-from-amnesia, but risky for navigation.

`foldspine.py` is a first non-destructive audit spine. It does not collapse historical files yet. It checks that the current rev0028 path is visible from:

- modules;
- tests;
- current docs;
- `PUBLIC_SURFACE.json`;
- `HEAD_REGISTRY.json`;
- `docs/00-index.md`;
- `surfaceledger.py`.

The refactor goal is to move from many ad-hoc folds toward one revision-aware spine while keeping old branchlets mapped.

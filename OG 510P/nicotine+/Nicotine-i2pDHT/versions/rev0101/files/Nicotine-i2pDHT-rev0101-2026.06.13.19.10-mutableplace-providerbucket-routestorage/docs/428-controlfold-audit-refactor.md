# controlfold audit/refactor

`controlfold.py` is the rev0041 current-revision fold audit.

It checks that the live rev0041 control path is visible through:

- current modules;
- current tests;
- current docs;
- `PUBLIC_SURFACE.json`;
- `HEAD_REGISTRY.json`;
- `docs/00-index.md`;
- `foldmap.py`;
- `foldregistry.py`;
- `surfaceledger.py`.

It also preserves rev0040 `operationsfold` as predecessor history.

Audit purpose: avoid creating another strong branchlet that works in tests but disappears from wake-from-amnesia navigation.

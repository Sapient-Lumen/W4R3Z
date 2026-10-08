# negotiationfold audit/refactor

`negotiationfold.py` is the rev0033 current-revision fold audit.

It verifies that the current surfaces are reachable from:

- modules;
- tests;
- docs;
- `PUBLIC_SURFACE.json`;
- `HEAD_REGISTRY.json`;
- `docs/00-index.md`;
- `surfaceledger.py`;
- `foldmap.py`.

It also preserves `scopefold.py` / rev0032 as predecessor history. The audit/refactor direction is to keep folding current surfaces into a declarative spine, but not to delete wake-from-amnesia trail markers that still explain why earlier seams exist.

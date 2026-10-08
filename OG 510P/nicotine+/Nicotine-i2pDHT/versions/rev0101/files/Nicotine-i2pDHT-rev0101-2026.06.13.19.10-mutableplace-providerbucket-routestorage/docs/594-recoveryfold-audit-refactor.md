# recoveryfold audit/refactor

`recoveryfold.py` pins the rev0056 path through source, tests, docs, fold map, fold registry, surface ledger, and the rev0055 `restartfold` predecessor.

This revision also tightens wake-from-amnesia discipline: the current path is not just larger; it is findable from `README.md`, `START_HERE.md`, `docs/00-index.md`, `PUBLIC_SURFACE.json`, `HEAD_REGISTRY.json`, and the active ledger surfaces.

The fold does not claim production safety. It only makes the active toy protocol surfaces visible and regression-checkable.

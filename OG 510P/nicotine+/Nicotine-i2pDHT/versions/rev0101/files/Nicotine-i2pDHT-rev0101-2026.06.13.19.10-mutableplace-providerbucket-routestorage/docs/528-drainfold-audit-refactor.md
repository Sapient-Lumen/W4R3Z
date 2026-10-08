# drainfold audit/refactor

`drainfold.py` pins rev0050's current path:

```text
outboxdrain
samcanary
compactjoin
drainfold
```

It also checks the rev0049 predecessors:

```text
publishdryrunfold
outboxfold
```

This audit is intentionally narrow. It ensures the next public-edge seam is visible from tests, docs, `PUBLIC_SURFACE.json`, `HEAD_REGISTRY.json`, fold map, fold registry, and active surface ledger. Historical branchlets remain preserved by older folds; rev0050 should not silently become another unindexed branch.

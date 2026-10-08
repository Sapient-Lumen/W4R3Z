# Foldmap audit/refactor

`foldmap.py` is the first declarative fold-map surface.

Historical fold modules remain valuable because they preserve the path by which the cube learned each risk surface. But bespoke fold modules are becoming their own navigation debt. rev0031 keeps them and adds a map that says:

```text
current rev0031 surfaces -> probeledger, crisisroute, sketchboundary, foldmap
historical folds         -> keycrisisfold, foldseal, foldspine, branchmergefold
```

The audit checks:

- current modules exist;
- current tests exist;
- current docs exist;
- public surface, head registry, docs index, and surface ledger mention the current needles;
- rev0031 remains visible as the current revision.

This is not a full deletion/refactor. It is a safer bridge toward one declarative current/historical surface map.

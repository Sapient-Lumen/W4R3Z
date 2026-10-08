# rev0035 — startmatrix / telemetrydebt / routerharness

rev0035 treats startup as a joined risk boundary rather than a boolean.  The prior cube could say that safe-start, persistence, and a no-network SAM probe passed; this revision asks whether a future node may actually advance into a selected launch profile.

The strongest sentence:

```text
A launchable node is still not a safe profile until router assumptions, metadata budgets, and service intent bind to the same start capsule.
```

New surfaces:

- `startmatrix.py` — leaf/garden/bridge/offline profile matrix.
- `routerharness.py` — bundle-first/external-SAM/offline router harness classifier.
- `telemetrydebt.py` — retained veiled metrics as evidence, memory, and metadata debt.
- `startfold.py` — rev0035 audit/refactor fold preserving rev0034 `foldmerge`.

This remains a no-network design cube.  No live SAM socket is opened.

# Bridgeauditfold audit/refactor

`bridgeauditfold.py` is the rev0048 fold audit.

It checks that the current line is visible through:

- active source files;
- active tests;
- current docs;
- `PUBLIC_SURFACE.json`;
- `HEAD_REGISTRY.json`;
- `docs/00-index.md`;
- `README.md`;
- `START_HERE.md`;
- `foldmap.py`;
- `foldregistry.py`;
- `surfaceledger.py`;
- predecessor `publicationfold.py`.

This is deliberately mundane.  The cube is now large enough that invisible branchlets are a real design risk.  The fold audit is part of the protocol-design hygiene: wake-from-amnesia must know what the current seam is.

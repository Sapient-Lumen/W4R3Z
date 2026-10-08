# Handlerfold audit/refactor

`handlerfold.py` is the rev0053 current-path audit.

It checks that the handler capsule, side-effect journal, adapter fuzz, tests, and docs exist, then runs predecessor and registry checks:

```text
rev0052 edgefold predecessor
foldmap
foldregistry
surfaceledger
```

This is a deliberately mundane refactor surface. The cube is large enough that current-path drift is now a design risk. Fold audits keep active intent visible without deleting historical wake-from-amnesia material.

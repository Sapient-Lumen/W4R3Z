# Foldspine audit/refactor

The cube has many historical fold modules because it keeps branchlets instead of deleting them. That is useful for wake-from-amnesia, but it can also make the current path harder to see.

`foldspine.py` centralizes current revision checks:

- required rev0028 modules exist;
- current rev0028 test exists;
- current docs exist;
- public surface, head registry, README, START_HERE, and docs index point at rev0028;
- surface ledger has rev0028 entries;
- predecessor rev0027 branchmerge fold still passes.

Foldspine is not protocol authority. It is a revision navigation audit.

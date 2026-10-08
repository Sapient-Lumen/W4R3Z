# Surface-fold audit/refactor

`surfacefold.py` is a small navigation audit.  The cube intentionally keeps historical branchlets and duplicate names for wake-from-amnesia, but current surfaces need a clean path.

The fold audit checks:

- current public surface revision;
- packaged artifact stem;
- public entry paths;
- current revision docs;
- active surface-ledger entries;
- README / START_HERE revision visibility.

This is not a linter.  It is a guard against amnesia: the cube should be able to tell a returning reader where the current head is.

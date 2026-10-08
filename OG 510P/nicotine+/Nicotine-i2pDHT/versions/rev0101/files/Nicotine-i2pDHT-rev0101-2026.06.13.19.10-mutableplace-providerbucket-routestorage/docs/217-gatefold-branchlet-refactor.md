# Gatefold branchlet audit/refactor

rev0024 recovers an alternate branchlet that had implemented `interestmix.py`, `routeattest.py`, and `gateaudit.py`. The active rev0023 lineage had instead focused on range sketches, admission walls, namespace policies, and namespacefold audit.

Both branchlets were useful. The right refactor is not deletion; it is folding.

`gatefold.py` checks that the folded surfaces are visible from:

- active modules,
- active tests,
- active docs,
- `PUBLIC_SURFACE.json`,
- `docs/00-index.md`,
- `HISTORICAL_SUPERSESSION.json`,
- the active surface ledger.

This keeps wake-from-amnesia history without letting branchlets obscure the current path.

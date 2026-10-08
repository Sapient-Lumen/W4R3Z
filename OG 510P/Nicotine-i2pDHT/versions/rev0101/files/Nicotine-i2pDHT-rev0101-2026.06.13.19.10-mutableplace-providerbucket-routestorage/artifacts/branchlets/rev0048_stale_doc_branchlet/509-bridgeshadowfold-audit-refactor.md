# Bridgeshadowfold audit/refactor

`bridgeshadowfold.py` pins the rev0048 current path:

- `bridgeshadow.py`
- `auditquorum.py`
- `redressgc.py`
- `bridgeshadowfold.py`
- `tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py`

The audit also verifies public pointers, head registry, docs index, fold map, fold registry, surface ledger, and predecessor `publicationfold.py` from rev0047.

This revision also preserves alternate public-shadow and bridge-audit sketches as branchlet history instead of leaving them as active, conflicting tests.

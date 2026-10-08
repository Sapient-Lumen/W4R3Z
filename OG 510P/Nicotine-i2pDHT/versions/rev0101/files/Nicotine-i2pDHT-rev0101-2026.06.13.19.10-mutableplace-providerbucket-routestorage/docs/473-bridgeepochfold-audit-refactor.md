# Bridgeepochfold audit/refactor

`bridgeepochfold.py` is the rev0045 audit/refactor surface.

It checks:

- active rev0045 modules exist;
- active rev0045 tests exist;
- active rev0045 docs exist;
- public pointers mention the current needles;
- `foldmap.py`, `foldregistry.py`, and `surfaceledger.py` know rev0045;
- rev0044 `branchsealfold.py` still passes as predecessor history.

This continues the cube habit: every speculative feature must also be visible from the wake-from-amnesia spine.

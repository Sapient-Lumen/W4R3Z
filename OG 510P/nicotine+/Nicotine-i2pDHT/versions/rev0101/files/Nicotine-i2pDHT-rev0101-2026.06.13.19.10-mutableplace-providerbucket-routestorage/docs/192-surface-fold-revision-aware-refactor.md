# Surface-fold revision-aware refactor

rev0020 introduced `surfacefold.py`, but the current-doc detection still contained a rev0020-specific string.  rev0021 refactors that audit to use the requested revision parameter.

This matters because the cube is revision-driven.  An audit that passes only because it remembers yesterday's revision is the same class of mistake as a DHT accepting a signed-but-stale mutable head.

The active surface ledger now points at:

- `epochsplit.py`
- `storewire.py`
- `repairreplay.py`
- revision-aware `surfacefold.py`

The refactor is intentionally small and tested, not a broad cleanup sweep.

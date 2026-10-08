# moderationfold audit/refactor

`moderationfold.py` is the rev0046 current-path audit. It preserves the rev0045 bridge-epoch/key-receipt/shadow-fire predecessor while pinning the new moderation/redress/bridge-ledger surfaces.

This revision also cleans up duplicate rev0046 fold definitions left by branchlet drift in:

- `foldmap.py`
- `foldregistry.py`
- `surfaceledger.py`

The fold audit requires the current modules, tests, docs, public surface, head registry, docs index, fold map, fold registry, and active surface ledger to agree.

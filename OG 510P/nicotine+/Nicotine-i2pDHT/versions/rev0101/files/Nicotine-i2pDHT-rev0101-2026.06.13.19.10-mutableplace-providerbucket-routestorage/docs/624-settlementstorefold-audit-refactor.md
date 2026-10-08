# settlementstorefold audit/refactor

`settlementstorefold.py` pins rev0059 through source, tests, docs, public pointers, fold map, fold registry, and active surface ledger.

This fold deliberately keeps both rev0058 predecessors visible:

- `finalityfold.py` for finality / retry escrow / prune guard,
- `settlementfold.py` for settlement / attestation / tombstone repair.

The refactor choice is to fold the branchlet into active history instead of deleting it or letting it silently diverge.

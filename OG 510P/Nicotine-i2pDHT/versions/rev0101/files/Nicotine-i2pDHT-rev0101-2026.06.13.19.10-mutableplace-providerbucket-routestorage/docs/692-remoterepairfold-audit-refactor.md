# remoterepairfold audit/refactor

`remoterepairfold.py` pins the rev0065 active surfaces:

```text
remotewitnessledger
repairoutbox
conflictcooldown
remoterepairfold
```

It also verifies that the rev0064 `retrypublishfold` predecessor remains visible. This keeps the ACK/retry/repair line navigable rather than letting public-edge branchlets pile up as hidden code.

The audit checks source, tests, docs, fold map, fold registry, and surface ledger entries for the current revision.

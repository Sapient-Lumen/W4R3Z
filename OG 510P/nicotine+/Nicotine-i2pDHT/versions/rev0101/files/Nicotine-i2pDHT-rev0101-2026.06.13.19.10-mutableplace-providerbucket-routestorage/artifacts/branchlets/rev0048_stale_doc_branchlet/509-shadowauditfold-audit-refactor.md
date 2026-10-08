# shadowauditfold audit/refactor

`shadowauditfold.py` pins the rev0048 live path across source, tests, docs, public surface, head registry, fold map, fold registry, and surface ledger. It also preserves rev0047 `publicationfold` as predecessor history.

The refactor intent is simple: as public bridge surfaces multiply, the active path needs declarative current-revision visibility so branch debris does not masquerade as protocol code.

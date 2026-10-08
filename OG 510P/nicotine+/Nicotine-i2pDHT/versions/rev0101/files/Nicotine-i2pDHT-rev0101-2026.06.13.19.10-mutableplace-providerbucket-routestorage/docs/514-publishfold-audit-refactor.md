# publishfold audit/refactor

`publishfold.py` is the rev0049 fold audit.

It checks that the new modules, tests, and docs are visible through the public surface, head registry, docs index, fold map, fold registry, and surface ledger. It also calls the rev0048 `shadowauditfold` predecessor so the new public-side-effect lane does not accidentally sever the bridge-shadow/audit/redress history.

This is deliberately an audit/refactor surface, not a protocol feature.

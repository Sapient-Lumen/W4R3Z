# repairpublishfold audit/refactor

`repairpublishfold.py` is the rev0066 fold audit.  It checks that the current repair-publish / ACK / duplicate-closure path is visible from source, tests, docs, fold map, fold registry, and surface ledger.

It also preserves rev0065 `remoterepairfold` predecessor history.  The refactor goal is to keep the public-edge repair lineage navigable as the cube grows.

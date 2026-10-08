# Publicedgefold audit/refactor

`publicedgefold.py` is the rev0050 fold audit. It keeps the active public-edge path visible across source, tests, docs, public pointers, fold map, fold registry, and surface ledger.

It also preserves the predecessor path:

- rev0049 `outboxfold.py`
- public outbox staging
- audit-gap repair planning
- publish dry-run and compaction branchlets retained as active history

The refactor goal is not deletion. The cube has valuable branch history. The goal is to prevent the current public-edge protocol seam from being hidden under older branchlet names.

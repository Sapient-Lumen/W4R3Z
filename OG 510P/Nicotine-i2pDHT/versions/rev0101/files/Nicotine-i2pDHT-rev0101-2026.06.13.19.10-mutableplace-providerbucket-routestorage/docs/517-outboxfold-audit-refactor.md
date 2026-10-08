# outboxfold audit/refactor

`outboxfold.py` pins the rev0049 active surface:

```text
publicoutbox
auditgap
outboxfold
tests/test_rev0049_publicoutbox_auditgap_fold.py
```

It also checks public pointers, head registry, docs index, fold map, fold registry, surface ledger, and the rev0048 `shadowauditfold` predecessor path.

The audit/refactor move is small but important: publication-related branch growth now has one active current fold instead of silently relying on previous publication, bridge-shadow, audit-quorum, or redress-GC folds.

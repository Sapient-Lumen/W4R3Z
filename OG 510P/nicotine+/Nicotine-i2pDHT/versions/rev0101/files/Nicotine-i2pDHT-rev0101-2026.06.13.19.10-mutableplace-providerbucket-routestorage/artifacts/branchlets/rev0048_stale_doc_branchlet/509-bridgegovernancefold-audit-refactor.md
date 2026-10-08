# rev0048 bridgegovernancefold audit/refactor

`bridgegovernancefold.py` is the canonical rev0048 fold after reconciling the shadowauditfold / bridgeaudit branchlets.

It pins the current bridge-shadow, audit-quorum, and redress-GC surfaces through source, tests, docs, public pointers, head registry, fold map, fold registry, and surface ledger, while keeping older branchlet names as historical wake-from-amnesia context.

Current test surface: `tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py`.

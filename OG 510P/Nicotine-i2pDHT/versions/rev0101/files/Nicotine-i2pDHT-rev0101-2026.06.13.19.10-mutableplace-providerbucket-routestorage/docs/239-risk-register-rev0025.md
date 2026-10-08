# Risk register — rev0025

| Risk | Current pressure test | Remaining debt |
|---|---|---|
| Namespace validation bypasses authorization | `capgate.py` requires capability validation after namespace dispatch | Need richer capability verbs/resources and production revocation-head semantics |
| Valid capability bypasses overload policy | `capgate.py` runs admission after capability validation | Need merged queueforge/admissionwall/gardenscheduler model |
| Useful refusal becomes reputation/payment | Admission receipts remain local evidence only | Need negative tests for refusal laundering across gardens |
| Evidence memory grows unbounded | `evidencegc.py` byte budgets, family caps, expiry, pinned hard evidence | Need multi-round evidence compaction and persistence model |
| Tombstones/forks forgotten too early | Pinned hard evidence survives ordinary expiry pressure | Need durable local storage and witness-repair integration |
| Partition merge accepts convenient latest head | `splitmerge.py` requires prev-link and diversity pressure | Need larger churn/partition simulations and garden witness integration |
| Audit drift | `riskfold.py` and surface ledger include rev0025 paths | Need periodic consolidation of many historical fold modules |

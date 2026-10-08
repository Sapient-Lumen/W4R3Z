# Branchlet fold audit/refactor

rev0024 includes an explicit audit/refactor lane: branchlets are folded, mapped, and tested rather than deleted or silently left to rot.

The fold makes these previously under-surfaced pieces visible:

- `interestledger.py` — an interest ledger for repeated metadata-budget pressure over time;
- `pressureledger.py` — a pressure ledger for repeated-round local evidence memory;
- `regionreceipt.py` — region receipt accounting for garden sweep work;
- `clockguard.py` — clock guard for TTL/skew/sequence/fork pressure;
- `relayticket.py` — relay ticket admission objects for garden capacity;
- `gossipsieve.py` — gossip sieve admission before expensive work;
- `branchletfold.py` — the audit surface that checks docs, tests, and surface-ledger visibility.

`branchletfold.py` is intentionally small. It does not audit the whole cube. It asks whether a named set of branchlet modules has code, a tested symbol, a documentation fragment, and active-surface-ledger visibility.

Design rule:

```text
Speculative branchlets are allowed; invisible branchlets are debt.
```

# rev0025 — capgate / evidencegc / splitmerge

rev0025 starts from three risky places that had been separated for too long:

1. capability-gated dispatch after namespace validation,
2. local evidence retention and garbage collection,
3. mutable epoch partition merge after split-brain observations.

The design sentence for this revision is:

```text
A valid local step is not a valid dispatch, and useful memory is not useful if it grows without pressure.
```

## What became executable

- `capgate.py` joins namespace-policy dispatch, capability-chain validation, revocation heads, and admission budgets.
- `evidencegc.py` models retention of hard negative evidence while soft convenience evidence expires or falls to budget pressure.
- `splitmerge.py` models split-brain recovery for signed mutable epoch heads observed through partition-labeled paths.
- `riskfold.py` audits whether the new joined risk surfaces are visible from code, tests, docs, public surface, head registry, and surface ledger.

## Why these surfaces are hard

The dangerous failures sit between components:

- a namespace policy accepts a payload, but the actor has no valid delegated capability;
- a capability chain is valid, but the garden is overloaded and must refuse usefully;
- a witness or tombstone is valuable, but retaining every receipt forever becomes a memory attack;
- two partitions reconnect, and the newest signed mutable head is tempting but under-diverse, forked, or not linked to local memory.

rev0025 does not try to solve global truth. It makes these local judgments explicit and testable.

## Nonclaims

No live I2P/SAM transport is implemented. No production DHT is implemented. No production authorization, evidence-GC, or partition-merge protocol is implemented. Family/path/partition labels are deterministic test hints, not proven independence.

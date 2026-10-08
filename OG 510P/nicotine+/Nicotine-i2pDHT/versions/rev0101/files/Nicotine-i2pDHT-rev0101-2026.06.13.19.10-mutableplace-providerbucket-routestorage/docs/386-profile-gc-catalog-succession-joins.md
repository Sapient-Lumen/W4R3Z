# Profile GC and catalog succession joins

Two folded branchlet surfaces matter because they protect service memory across time:

`profilegcjoin.py` prevents profile garbage collection from deleting restart-critical hard negatives or checkpointed facts merely because profile GC itself looked safe.

`catalogsuccession.py` prevents a successor catalog from being accepted merely because it verifies. It joins key-crisis evidence, previous-catalog linkage, sequence advance, profile/router binding, and service downgrade pressure.

The design guess:

```text
A garden service catalog is mutable local memory. Upgrade, restart, GC, and key-crisis events are all service-continuity boundaries.
```

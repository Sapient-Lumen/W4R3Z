# Wake from amnesia — rev0062

Start here after forgetting the context:

1. rev0061 created a terminal delivered-send lane: delivery settlement, ACK archive, ACK prune join.
2. A sibling rev0061 branchlet explored missing-ACK repair: delivery repair, rollback probe, live egress retry/withdraw.
3. rev0062 folds that branchlet into active source and adds the missing joined boundary.
4. `ackrepairjoin.py` decides whether the object is terminal ACK, retry repair, withdraw repair, or contradiction.
5. `retryfence.py` makes retry/withdraw readiness restart-sticky.
6. `repairpruneguard.py` prevents ACK pruning from deleting repair debt.

Mantra:

```text
ACK, retry, withdraw, prune, and restart memory are five different permissions.
```

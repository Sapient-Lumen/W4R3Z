# Delta repair tombstone-first join — rev0030

`deltarepairjoin.py` joins range-delta sketch reports to egress-budget pressure and exact repair replies. It keeps the cube from treating a compact delta sketch as final truth.

The important path is tombstone-first repair. If the remote range says tombstones are missing, the join keeps the repair window open until exact tombstone material arrives or the repair request is rejected. A sketch can request repair; it cannot bury deletion, compromise, or revocation evidence behind ordinary provider churn.

Nonclaim: `deltasketch.py` is still an exact toy sketch surface, not Minisketch, IBLT, or a privacy-preserving set reconciliation implementation.

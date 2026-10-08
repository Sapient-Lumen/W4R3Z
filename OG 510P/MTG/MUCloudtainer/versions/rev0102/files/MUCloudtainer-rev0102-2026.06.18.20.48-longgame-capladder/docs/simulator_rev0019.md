# rev0019 simulator status

rev0019 does not add new Magic rules. It adds a stronger bridge for proving that C++ transition code matches the Python reference on recorded public-game traffic.

Current simulator status:

```text
Python automated simulator: working beta
Python public DecisionFrame/replay/promotion gates: working beta
C++ deck-probe kernel: working acceleration
C++ legal-menu kernel: differential-tested subset
C++ transition kernel: broad one-action subset
C++ recorded-trace checker: new in rev0019
Full C++ rollout core: not yet
```

The simulator is now close to the point where learning/evolution experiments can become more serious, but promoted claims should still include:

```text
simulator revision
interface type
reward convention
truncation status
replay sample status
C++ trace-check status when relevant
```

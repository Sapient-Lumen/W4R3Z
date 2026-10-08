# rev0046 simulator status

The simulator itself is unchanged in this revision.  The new work is on the label-selection layer above the referee.

Current trust pattern:

```text
public DecisionFrame agents choose legal actions
Python referee applies authoritative transitions
offline branch labeler may copy hidden true state
C++ transition microkernel checks Python transitions in shadow
promotion/reward/statistical gates remain separate
```

rev0046 produced zero branch truncations and zero C++ transition mismatches in the new matched queue audit.

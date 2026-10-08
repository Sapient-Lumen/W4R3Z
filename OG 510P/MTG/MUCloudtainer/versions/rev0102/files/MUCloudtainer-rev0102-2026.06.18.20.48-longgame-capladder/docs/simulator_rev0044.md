# simulator status at rev0044

The simulator remains an automated beta suitable for audited learning infrastructure experiments.  It is not yet a final source of MUC theory.

rev0044 does not change card rules or gameplay semantics.  It changes label collection infrastructure:

```text
public frame screen -> selected hidden-state branch labeler -> C++ shadow transition check
```

The semantic rule stays:

```text
Python referee is authoritative.
C++ may accelerate only after parity checks.
Public agents and screeners receive only public DecisionFrames.
```

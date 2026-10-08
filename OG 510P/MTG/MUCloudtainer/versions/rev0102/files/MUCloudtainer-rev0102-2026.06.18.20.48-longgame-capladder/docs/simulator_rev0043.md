# Simulator status rev0043

rev0043 does not change card rules or legal action generation. It changes how offline counterfactual labels are collected from the simulator.

The simulator continues to provide:

```text
public DecisionFrame
legal action list
hidden true state inside the referee only
Python semantic state transition
C++ shadow parity check
```

The new collector uses copied referee states to branch actions from the same public situation. That is an offline data-generation privilege, not an agent privilege.

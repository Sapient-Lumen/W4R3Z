# Simulator notes rev0045

No simulator rules changed in rev0045. The revision exercises the current simulator through a matched queue-selection counterfactual audit:

```text
public DecisionFrame collection
public-only queue ranking
hidden-state offline branch labels
C++ transition shadow check
```

The run produced zero branch truncations and zero C++ transition mismatches, so no new simulator correctness issue surfaced in this revision.

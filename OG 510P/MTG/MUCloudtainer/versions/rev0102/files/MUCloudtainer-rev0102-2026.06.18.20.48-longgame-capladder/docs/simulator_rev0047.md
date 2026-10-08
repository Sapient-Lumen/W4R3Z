# Simulator Notes rev0047

No core Magic-rule semantics were intentionally changed in rev0047.

The relevant simulator-facing work is methodological:

```text
public frame selection
  -> offline hidden-state branch labels
  -> C++ transition shadow parity
  -> public-ranker payoff evaluation
```

This preserves the hidden-information boundary: policies see public `DecisionFrame`s; the offline labeler uses true state only to compare legal alternatives from the same referee position.


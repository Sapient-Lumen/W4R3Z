# simulator rev0050

No card-rule semantics changed in rev0050.

The simulator was exercised through:

```text
256 terminal-clean public games
8 deterministic replay samples
76,375 live C++ shadow transition checks
1,872 replay C++ trace checks
```

All payoff rows were terminal-clean at `max_decisions=900`.  This revision is a comparison-analysis revision rather than a rules-engine revision.

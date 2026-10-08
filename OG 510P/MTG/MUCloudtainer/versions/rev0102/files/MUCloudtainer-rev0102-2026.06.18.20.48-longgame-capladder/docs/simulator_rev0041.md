# Simulator status after rev0041

The simulator remains an automated beta suitable for public-agent smoke payoff tables, replay traces, C++ transition shadowing, and offline counterfactual label generation.

rev0041 did not change card semantics. It changed how branch-label situations are selected:

```text
public behavior game
  -> public hard-frame screen
  -> hidden referee copy for offline branches
  -> public-agent branch rollouts
  -> C++ transition shadow check
```

No gameplay agent receives hidden state.

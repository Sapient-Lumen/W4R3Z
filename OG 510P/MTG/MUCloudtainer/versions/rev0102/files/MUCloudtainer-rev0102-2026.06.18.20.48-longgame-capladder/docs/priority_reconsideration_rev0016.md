# rev0016 priority reconsideration

The priority order changed after the C++ discussion.

## Current priorities

```text
1. Differential C++ legal-menu harness             done in rev0016
2. C++ state-transition microcases                 next
3. Sequential racing / candidate pruning           started in rev0016
4. C++ rollout skeleton behind replay gates        later
5. Alpha-Rank / meta-rank over promoted tables     later
6. Tiny action-feature imitation/ranker            later
```

## Why C++ legal menu before C++ rollout?

Legal-menu enumeration is where the referee tells learning methods what they are allowed to do. A fast but wrong menu would poison every downstream experiment. A no-mutation C++ legal-menu kernel is easier to differential-test than a full C++ state transition engine.

## Why sequential racing now?

The constructor space is small enough to enumerate but too large to deeply evaluate every deck-pilot-mulligan bundle. Racing gives us a way to spend rollout budget adaptively while still labeling uncertainty and truncation status.

## What still should wait

Neural RL should still wait. We now have action features and public DecisionFrames, but the simulator/C++ bridge and payoff-selection gates are higher leverage.

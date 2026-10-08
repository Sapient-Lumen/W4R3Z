# Simulator status in rev0035

The Python simulator remains the semantic authority.  rev0035 did not change
card rules or turn structure.  The new work is entirely around how offline
counterfactual labels are sampled from legal DecisionFrames.

The simulator now supports three action-label collection modes:

```text
ordinary public games
outcome-weighted trajectories
branched action counterfactuals
```

rev0035 extends the third mode with budgeted high-action frame sampling.  This is
not a gameplay simplification.  All branch actions still come from the exact
legal menu emitted by the referee.  The simplification is only in how many legal
actions the offline labeler can afford to roll out.

Working status:

```text
automated simulator:             working beta
learning-loop simulator:         usable under gates
tournament-claim simulator:      still requires denser samples and confidence labels
C++ tournament core:             not authoritative yet
```

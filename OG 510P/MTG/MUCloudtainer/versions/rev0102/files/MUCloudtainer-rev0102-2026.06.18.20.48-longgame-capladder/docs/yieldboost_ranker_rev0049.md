# rev0049 yield-screened ranker refresh

rev0049 keeps the yield-screened online action-counterfactual collector from
rev0047, adds one more small batch of audited labels, and retrains a JSON-backed
linear counterfactual action ranker:

```text
public hard-frame pool
  -> yield-screen queue
  -> hybrid action subset
  -> online adaptive branch racing
  -> C++ transition shadow check
  -> public action-feature ranker
```

The ranker is still not an RL policy.  It is a small supervised scorer trained
from branch rollout labels.  The important boundary remains unchanged: gameplay
agents receive only `DecisionFrame.observation` and legal actions.  Hidden state
is used only by the offline branch-label referee after a public situation has
already been selected.

This revision's main evaluation improvement is not a more complex model; it is
that the payoff panel is terminal-clean from the start rather than repaired after
a low-ceiling smoke run.

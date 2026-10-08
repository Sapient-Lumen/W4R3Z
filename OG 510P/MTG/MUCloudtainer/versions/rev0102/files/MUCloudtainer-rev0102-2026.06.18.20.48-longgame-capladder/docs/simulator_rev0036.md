# simulator rev0036

No card-rule semantics changed in rev0036.

The simulator work this turn is around the learning/audit shell:

```text
public DecisionFrame behavior game
copy exact true referee state offline
branch legal action candidates
allocate extra branch rollouts adaptively
roll out with public agents
C++-check every branch transition
train/evaluate a public-safe ranker
```

The legal-action contract remains unchanged: the engine/referee emits legal macro-actions, and agents rank those legal actions.  Hidden state is used only by the offline labeler and never shown to the policy.

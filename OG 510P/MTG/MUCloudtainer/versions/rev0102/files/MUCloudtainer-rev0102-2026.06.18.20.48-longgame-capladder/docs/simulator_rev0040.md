# Simulator notes — rev0040

No gameplay rule changed in rev0040.

The simulator/referee contract remains:

```text
true GameState stays inside the engine/referee
public DecisionFrame goes to agents
legal action list is exact
agents return legal action indices
Python is semantic authority
C++ checks transition signatures in shadow
```

The new code operates above the simulator as an offline labeler. It copies the true state only inside the counterfactual labeling harness, branches legal actions, rolls out public agents, and C++-checks the resulting transition stream.

This preserves the project boundary: learned/search methods do not get hidden state during play.

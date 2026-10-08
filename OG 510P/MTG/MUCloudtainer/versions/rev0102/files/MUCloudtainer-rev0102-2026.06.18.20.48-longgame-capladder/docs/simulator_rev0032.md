# Simulator status at rev0032

The simulator is now a Python-authoritative MUC-5 referee with replay, promotion, statistical, reward, public-observation, and C++ parity gates.

rev0032 does not change card semantics. It changes the performance/safety boundary around forced no-choice frames:

```text
DecisionFrame with exactly one legal action
  ↓
Python applies authoritative transition
  ↓
C++ receives the same forced-action segment
  ↓
C++ end SIGv2 must match Python end SIGv2
```

This lets us measure a future compression seam without exposing agents to hidden state or allowing C++ to become authoritative prematurely.

The key simulator improvement this turn is that segment-shadow payoff rows now include the same promotion columns as ordinary public payoff rows. This means C++-checked performance experiments can be admitted or rejected by the same gates as learning experiments.

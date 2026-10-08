# rev0033 C++ combat sentinel fix

rev0033 found a real C++ parity bug while evaluating the new counterfactual-ranker traffic.

The C++ transition kernel uses `-1` as the sentinel for "no Jace". Combat damage exposed a collision:

```text
Jace at 4 loyalty
one unblocked Overlord attacks Jace for 5
4 - 5 = -1
```

That exact value looked like the "no Jace" sentinel before the state-based check could put Jace into the graveyard. Python correctly moved Jace to the graveyard and cleared `jace_used_this_turn`; C++ failed to do so in that edge case.

The fix is local to combat resolution:

```text
when combat damage reduces Jace loyalty to <= 0:
  add Jace to graveyard
  set loyalty sentinel to -1
  clear jace_used_this_turn
```

A directed pytest now covers this edge case and compares the C++ transition signature to Python's authoritative post-state signature.

This is the exact reason the C++ doctrine remains:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = fast kernel candidate, trusted only after differential parity checks
```

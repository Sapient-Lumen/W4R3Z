# rev0034 simulator note

No new Magic rule was added in rev0034.  The simulator change is about measurement:

```text
ActionCounterfactual candidate rows now carry label-noise fields.
```

This helps distinguish simulator correctness from policy-learning noise.  The rules engine remains Python-authoritative, with C++ shadow checks attached to branch and payoff traffic.

The game is still MUC-5:

```text
Island
Counterspell
Force of Will
Jace, the Mind Sculptor
Overlord of the Floodpits
```

Decks are still arbitrary-count 40- or 60-card lists over those five cards.

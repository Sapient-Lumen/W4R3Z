# simulator status rev0025

No new card rules were added in rev0025.  The simulator change is evaluative: outcome-trained traffic now exercises the same public DecisionFrame/referee path as earlier code, MLP, and mulligan agents.

Current simulator confidence:

```text
automated public play:       green for smoke/race experiments
learned policy evaluation:   green under promotion/replay/C++ gates
strategic claims:            still yellow until payoff tables are denser
full C++ authority:          not yet
```

The new outcome-ranker payoff table had:

```text
256 public games
0 truncations
8 replay samples passed
1,943 C++ trace events checked
0 skipped events
0 mismatches
```

That supports continued policy experiments without changing the rules surface.

# rev0022 ranker/race result notes

The ranker sequential race and MAP-Elites ranker-variant table both passed their gates in this revision.

The most important result is not which strategy topped a smoke table. It is that the evaluation stack now supports this full chain:

```text
frozen ranker policy
+ blended ranker policy
+ readable code policy
+ public profile policy
+ deck/mulligan bundle
+ staged race or same-deck pilot comparison
+ promotion/statistical/replay/C++ trace checks
```

Interpretation rule:

```text
Smoke tables can eliminate bad ideas.
They cannot certify optimal play.
```

The ranker family remains a baseline learning bridge, not a final method. Its failures are useful because they identify whether action features, imitation data, or deck/pilot interaction is the next bottleneck.

# rev0047 Yield-Ranker Payoff Results

The rev0047 ranker panel ran six strategy bundles through the public payoff/replay/C++ gate:

```text
payoff games:          144
aggregate rows:        72
replay samples:        8 / 8 passed
C++ shadow events:     41,437
C++ skipped events:    0
C++ mismatches:        0
promotion gate:        passed
statistical gate:      passed
```

There were 30 truncations. This is under the configured gate threshold, but it is high enough that draw-half scores should be treated as reporting-only for this panel. Do not use this smoke table as training reward.

No MUC-theory claim should be made from this table. The result exists to prove that a yield-screen-trained ranker can enter the same public strategy population as code policies, outcome rankers, and previous counterfactual rankers.


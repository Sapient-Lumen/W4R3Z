# rev0036 adaptive racing results

rev0036 trained `counterfactual_linear_ranker_rev0036` from adaptive/racing branch labels.

Holdout smoke metrics:

```text
test rows:                     6
test RMSE:              ~0.4121
test top-1 best action: ~0.6667
random best baseline:   ~0.6667
test MRR:               ~0.8333
```

The top-1 number is not evidence of improvement because the baseline is also high in this tiny holdout.  The useful result is that the label collector found decisive situations, avoided branch truncations, and recorded adaptive allocation metadata.

The payoff smoke panel:

```text
strategies:               4
payoff games:            64
replay samples:       8 / 8 passed
C++ shadow events:   18,599
C++ mismatches:           0
truncations:              0
promotion gate:        passed
statistical gate:      passed
```

The payoff table is smoke-scale.  It proves the new policy aliases and gates work; it does not make a matchup claim.

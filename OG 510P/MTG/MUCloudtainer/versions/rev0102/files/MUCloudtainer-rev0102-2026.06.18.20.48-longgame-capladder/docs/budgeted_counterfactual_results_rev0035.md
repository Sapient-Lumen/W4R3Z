# rev0035 budgeted counterfactual ranker results

rev0035 trains a linear public action ranker from the budgeted branch labels:

```text
counterfactual_linear_ranker_rev0035
counterfactual_ranker_blend_threat_rev0035
counterfactual_ranker_blend_counter_rev0035
counterfactual_ranker_blend_patient_rev0035
```

Training target:

```text
public context features + public legal-action features
  -> mean actor score from branch rollouts
```

Sample weighting:

```text
(0.20 + label_confidence_proxy) * subset_discount
```

where subset labels get a small discount because they only compare against the
branched budget, not the full legal menu.

## Smoke metrics

```text
training rows:       63
test rows:           23
train situations:    18
test situations:      8
test RMSE:       ~0.300
test R^2:        ~0.603
```

The top-1 metrics are not very meaningful in this smoke run because most labels
were ties; the random best-action baseline was also 1.0.  The model artifact is
therefore useful as a pipeline object, not as a claim of strength.

## Public payoff smoke table

```text
strategies:             6
payoff games:          144
aggregate rows:         72
promotion gate:       pass
statistical gate:     pass
replay samples:       8 / 8 pass
C++ shadow events:    42141
C++ skipped events:       0
C++ mismatches:           0
truncations:              7
```

The truncations are below the promotion/statistical gate threshold, but they
remain a warning: draw-half score is reporting-only on those rows and must not be
used as a positive training reward.

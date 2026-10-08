# rev0029 experiment matrix additions

New experiment axes:

```text
mulligan policy:
  keep_always
  land_band
  land_band_business
  mulligan_ranker_rev0024
  mulligan_outcome_ranker_rev0027
  mulligan_counterfactual_ranker_rev0029

counterfactual target:
  first-look keep vs first-look mulligan

C++ batching diagnostic:
  forced DecisionFrame rate
  pass-only frame rate
  forced-run length
  estimated segment compression ratio
```

Suggested next matrix:

```text
opening hand × deck shell × life total × play/draw × repeated branch rollouts
```

The repeated-rollout version should output mean branch value and uncertainty, rather than a single win/loss comparison.

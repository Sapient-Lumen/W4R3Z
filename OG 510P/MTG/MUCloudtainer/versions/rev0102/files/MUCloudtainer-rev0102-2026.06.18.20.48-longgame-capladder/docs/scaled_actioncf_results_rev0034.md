# rev0034 scaled action-counterfactual results

This file is populated conceptually by `data/rev0034_scaled_action_counterfactual_summary.json`.

Interpretation rules:

```text
If promotion/statistical/replay/C++ gates pass:
  the data is usable for further experiments.

If a ranker tops a smoke table:
  it is a candidate, not a claim.

If label confidence is low:
  collect more branch rollouts before making policy claims.
```

The important result to inspect is not just standings.  Inspect:

```text
label_audit.mean_label_confidence_proxy
counterfactual_collection.behavior_chosen_best_rate
training_summary.test_top1_best_action_accuracy
training_summary.test_random_best_action_baseline
cpp_shadow_summary.mismatches
cpp_shadow_summary.skipped_events
```

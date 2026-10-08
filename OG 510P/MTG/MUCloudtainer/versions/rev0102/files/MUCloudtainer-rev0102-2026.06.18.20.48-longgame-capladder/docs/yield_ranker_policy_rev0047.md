# rev0047 Yield-Screened Counterfactual Ranker

rev0047 trains a new public action ranker:

```text
counterfactual_linear_ranker_rev0047
counterfactual_ranker_blend_threat_rev0047
counterfactual_ranker_blend_counter_rev0047
counterfactual_ranker_blend_patient_rev0047
```

The ranker is trained from the accumulated audited action-counterfactual label corpus plus the new rev0047 yield-screened rows. It uses the same public context/action feature interface as earlier rankers and is stored as JSON:

```text
data/rev0047_counterfactual_action_ranker_model.json
```

## Refactor

The repeated Ridge-training blocks from prior action-counterfactual scripts are now factored into:

```python
train_linear_action_ranker_from_candidate_rows(...)
```

in:

```text
src/muc5/ranker_policy.py
```

That function takes already-public feature rows, splits by situation id, trains a small linear ranker, and returns the model, metrics, coefficient rows, and prediction rows. It does not inspect `GameState`.

## Smoke metrics

The archived rev0047 model reports:

```text
training rows:                 448
test rows:                     160
train situations:              100
test situations:               39
test top-1 best-action acc:    0.718
random best-action baseline:   0.681
test decisive top-1 acc:       0.400
test MRR:                      0.823
```

The model is a valid experimental policy, not a strategic breakthrough. The decisive-situation metric is still weak, which reinforces the current priority: better labels before fancier models.


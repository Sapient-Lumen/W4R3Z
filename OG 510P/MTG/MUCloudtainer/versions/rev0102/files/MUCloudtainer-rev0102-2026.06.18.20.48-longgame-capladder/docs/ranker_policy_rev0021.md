# rev0021 — frozen public action-ranker policy

rev0020 created an imitation dataset.  rev0021 turns that supervised artifact into a real public policy:

```text
DecisionFrame.observation
+ one legal Action
  -> context features + action features
  -> frozen linear score
```

The policy is intentionally simple:

```text
linear_ranker_rev0021 = intercept + dot(coefficients, public_safe_features)
```

It is not meant to be a strong agent yet.  It is a bridge test:

1. Can we collect legal-action candidate data without hidden-state leakage?
2. Can we train a small ranker from public policies?
3. Can the ranker enter the same payoff/promotion/statistical gates as hand-coded policies?
4. Can future neural/ranking policies use the same feature interface?

The model lives at:

```text
data/rev0021_linear_ranker_model.json
```

and is loaded by:

```text
make_public_agent("linear_ranker_rev0021")
```

The model file is deliberately JSON, not pickle.  Future sandpeople should be able to inspect the features, coefficients, intercept, source revision, and training summary without executing arbitrary code.

## Important caution

This policy imitates weak/readable policies.  A high top-1 imitation score does not mean strong play.  It only means the features and wrapper can reproduce the training population often enough to be worth testing in promoted payoff tables.

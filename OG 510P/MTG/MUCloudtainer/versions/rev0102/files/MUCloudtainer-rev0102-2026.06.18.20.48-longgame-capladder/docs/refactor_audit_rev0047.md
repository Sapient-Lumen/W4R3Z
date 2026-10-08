# rev0047 Refactor and Audit Notes

## Refactor

New module:

```text
src/muc5/action_yield_collect.py
```

It separates yield-screen production collection from the rev0046 matched queue audit. The matched audit remains useful for comparing selectors; the rev0047 collector is the path for producing new labels from the current best queueing model.

Shared training helper added:

```text
src/muc5/ranker_policy.py::train_linear_action_ranker_from_candidate_rows
```

This reduces duplicated Ridge-training code in future action-counterfactual scripts.

New strategy-set helper:

```text
src/muc5/strategy_sets.py::yield_counterfactual_action_ranker_bundles
```

Generic public-agent aliases already handle rev0047 ranker names through the rev0036 factory refactor.

## Audit gates

rev0047 audit checks require:

```text
rev0047 summary exists
candidate rows exist
C++ branch collection has zero skipped events and zero mismatches
ranker model exists and loads
payoff rows exist
payoff C++ shadow has zero skipped events and zero mismatches
promotion/statistical gates passed
required docs/scripts/tests exist
```


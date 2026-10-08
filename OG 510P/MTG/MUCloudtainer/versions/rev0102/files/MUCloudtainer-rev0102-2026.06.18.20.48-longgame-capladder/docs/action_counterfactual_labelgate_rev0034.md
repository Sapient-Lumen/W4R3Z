# rev0034 action-counterfactual label gate

Action-counterfactual labels are noisy because a branch rollout is still a stochastic game.  rev0034 adds a small label-gate/audit layer so future users do not confuse "one branch rollout happened to win" with "this action is known to be good."

For every sampled situation, the collector now records:

```text
best_mean_actor_score
second_best_mean_actor_score
situation_best_margin
label_confidence_proxy
```

For every action, it records:

```text
mean_actor_score
actor_score_stdev
value_gap_to_best
is_best_action
```

The `label_confidence_proxy` is intentionally named as a proxy.  It is computed from the empirical margin and rollout-score noise.  It is useful for filtering/training weights, but it is not a theorem.

## Why this matters

Earlier imitation-style rankers could only learn actions that a policy chose.  Outcome-weighted imitation learned from winning trajectories, but still could not evaluate unchosen alternatives.  Action-counterfactual labels are the first gameplay-learning seam that can say:

```text
The behavior policy chose action A.
The branch rollouts suggest action B was better from the same state.
```

The danger is overfitting noisy branch results.  rev0034 therefore archives the label noise instead of hiding it inside a model file.

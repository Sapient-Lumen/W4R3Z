# rev0034 scaled action-counterfactual ranker

rev0033 proved the branch-label seam for gameplay actions, but it was deliberately tiny.  rev0034 scales the same idea without changing the fairness contract:

```text
public DecisionFrame situation
  -> copy hidden true state inside offline labeler only
  -> branch each manageable legal action
  -> roll out each branch with public agents
  -> label the public action candidates with branch outcomes
```

The agent still never sees the hidden true state.  Hidden state is used only by the offline referee to ask the scientific question: "What happened when each legal action was tried from the same state?"

## Parameters

The archived build uses:

```text
behavior game limit:        14
sampled situations target:  40
max legal actions/frame:     8
branch rollouts/action:      3
branch rollout horizon:    240 decisions
```

This is still a small label budget.  It is larger than rev0033, but not enough to make strong strategic claims.  The important change is that every candidate row now carries label-noise diagnostics:

```text
actor_score_stdev
second_best_mean_actor_score
situation_best_margin
label_confidence_proxy
```

## Model

The frozen policy is:

```text
counterfactual_linear_ranker_rev0034
```

It is a Ridge linear scorer over the same public action-ranker feature interface used by previous rankers.  The training target is the mean actor score from branched public rollouts.  Rows are weighted by:

```text
0.25 + label_confidence_proxy
```

That is only a cheap proxy.  It is not a confidence interval and should not be cited as proof of correctness.

## Evaluation contract

The rev0034 ranker is evaluated as an ordinary public strategy-bundle component beside rev0033, outcome-weighted, MLP, public, and code-policy baselines.  Evaluation rows still pass through:

```text
promotion gate
statistical gate
replay samples
C++ shadow transition check
```

Python remains semantic authority; C++ remains a parity-checked accelerator candidate.

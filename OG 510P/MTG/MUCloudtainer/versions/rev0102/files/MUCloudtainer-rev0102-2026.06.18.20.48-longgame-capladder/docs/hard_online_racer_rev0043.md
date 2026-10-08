# rev0043 hard-frame online racer

rev0043 turns the previous hard-frame label audit into an online branch-budget collector.

Previous shape:

```text
select hard public frames
  ↓
generate a fixed branch rollout matrix
  ↓
compare fixed/adaptive labelers after the fact
```

New shape:

```text
select hard public frames
  ↓
choose a hybrid branch subset
  ↓
run one rollout for every selected legal action
  ↓
spend extra rollouts live on current best / runner-up actions
  ↓
record the final action labels and allocation history
```

The gameplay agent still receives only a public `DecisionFrame`. The offline label collector owns a copied true referee state only so it can run counterfactual branches from the same exact position.

## Archived smoke result

```text
behavior games:              20
behavior decisions:       3,370
choice frames seen:       1,725
candidate hard frames:      782
selected hard situations:    10
high-action selected:        10
mean action count:         14.2
branched actions:            50
branch games:                78
base rollouts:               50
adaptive extra rollouts:     28
early stops:                  3
branch truncations:           0
decisive situations:          4
decisive per 100 rollouts:  5.13
C++ checked transitions:  12,431
C++ skipped transitions:      0
C++ mismatches:               0
```

This is a label-system result, not a promoted gameplay policy.

## Why this revision matters

The rev0042 fixed-vs-adaptive audit showed that adaptive labels can save rollout budget, but it was still an after-the-fact audit over a fully generated matrix. rev0043 proves the actual online collector can spend rollout budget incrementally while preserving the same public/hidden-state boundary and C++ shadow parity gates.

## Pushback

The decisive-label yield is still modest. Four decisive situations from seventy-eight branch rollouts is useful, but it is not enough to train a strong gameplay ranker by itself. The next question is no longer "can online racing work?" It is:

```text
Which hard-frame score predicts decisive labels per rollout?
```

That suggests a margin-seeking screen that learns from the new `selected`, `allocation`, and `candidate` tables.

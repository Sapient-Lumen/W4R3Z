# rev0020 action-ranker seed

rev0020 adds the first learning-facing dataset that is deliberately smaller than RL: imitate existing public policies from legal action menus.

The target is not to discover MUC truth yet. The target is to create a stable supervised bridge:

```text
public DecisionFrame observation
+ legal action candidate
  ↓
context features + action features
  ↓
chosen / not chosen label from a public policy
```

This gives future sandpeople an easy way to test listwise action-ranking models before PPO, CFR approximators, or neural self-play.

## New files

```text
src/muc5/imitation.py
scripts/run_rev0020_action_ranker_seed.py

data/rev0020_action_ranker_dataset.csv
data/rev0020_action_ranker_coefficients.csv
data/rev0020_action_ranker_summary.json
```

## Feature contract

Features are intentionally public-safe:

```text
context features:
  frame / phase
  life fractions
  public mana counts
  public Jace/Overlord state
  stack depth
  own hand counts
  pending choice kind

action features:
  action kind
  cast card
  Force payment/pitch card
  target card
  Jace mode
  Overlord mode
  choice/discard card
  attack/block counts
```

No opponent hand, no opponent library order, no GameState object.

## Smoke dataset

The rev0020 collection used 48 public-agent games and produced:

```text
12,977 decision frames
28,867 candidate-action rows
12,977 chosen rows
81 numeric features
max legal action count: 22
mean legal action count: about 2.22
```

A simple scikit-learn logistic regression was trained only as a sanity check:

```text
test top-1 action accuracy: about 0.868
random slot baseline: about 0.717
test MRR: about 0.923
```

This is imitation of weak/readable policies, not learned strategic strength. It is useful because it proves the action-feature path can produce a model-shaped artifact from replayable public frames.

## Why now

This is deliberately earlier than neural RL. A supervised action-ranker seed is easier to audit:

```text
input rows are visible
features are named
labels come from named public policies
no reward convention is involved
no truncation exploitation can be rewarded
```

Later, the same feature contract can support policy distillation, neural best-response warm starts, or a tiny action-ranking policy inside promoted payoff tables.

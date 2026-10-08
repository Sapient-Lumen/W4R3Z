# rev0025 trajectory audit

Outcome-weighted learning creates a new risk: labels are allowed to know the future even though policies are not.  rev0025 isolates this by adding terminal labels after public rows are collected.

## What the agent sees

At decision time the behavior policy sees only:

```text
player-correct observation
legal macro-action list
local RNG for tie-breaks
```

## What the dataset receives after the game

After terminal resolution, every row receives:

```text
terminal
winner
loss_reason
actor_terminal_score
outcome_weight
```

The terminal label is not part of the observation.  It is a supervised-training target/weight.

## Truncation rule

Nonterminal truncations have `outcome_weight = 0.0`.  Draw-half reporting remains available in payoff tables, but truncation is not a positive teacher.  This preserves the rev0011 reward-guard logic: report draws separately, do not reward stalling unless an experiment explicitly says it is doing that.

## Why keep losing trajectories at low weight?

A pure win-only filter can produce brittle models that see too few difficult states.  rev0025 keeps terminal losses at weight 0.15 so the ranker still sees legal action structure from bad positions, but winners dominate.

Future experiments can compare:

```text
win-only
win/loss = 1.0/0.15
win/loss = 1.0/0.0
terminal score regression
advantage-weighted policy updates
```

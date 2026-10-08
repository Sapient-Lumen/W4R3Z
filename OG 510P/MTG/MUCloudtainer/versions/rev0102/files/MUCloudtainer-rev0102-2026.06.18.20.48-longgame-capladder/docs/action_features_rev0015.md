# rev0015 action-feature encoder

rev0015 adds:

```text
src/muc5/action_features.py
```

This is the first small bridge toward imitation learning, action ranking, and neural policies.

The current environment emits a dynamic legal-action list. That is the correct legality interface, but future neural methods should not learn from raw list positions alone, because slot `3` in one frame may be unrelated to slot `3` in another. The action-feature encoder gives each legal action a stable vector.

## Current features

Feature groups include:

```text
action kind one-hots
cast-card one-hots
Force payment and pitch-card flags
target-card flags
Jace mode flags
Overlord mode flags
choice-effect flags
choice-card flags
attack/block normalized counts
target Overlord state flags
pass-in-main / pass-in-response flags
```

The encoder consumes only the legal `Action` plus optional public observation metadata such as `frame`. It does not inspect `GameState`.

## Intended use

Near-term uses:

```text
public policy debugging
logistic/LightGBM action rankers
imitation datasets from code-policy or heuristic games
small PyTorch listwise policy/value prototypes
feature importance audits
```

Later neural agents should receive:

```text
public observation features
+ legal action feature matrix
+ legal action mask/list
```

not omniscient state and not raw action slots alone.

# rev0023 — refactor and audit notes

## Refactor

The main refactor is in `ranker_policy.py`: the JSON-backed ranker model family now contains both linear and one-hidden-layer MLP models.

The agent factory in `public_agents.py` recognizes MLP policies, but the fairness boundary is unchanged:

```text
public agent receives DecisionFrame only
public agent returns legal action index
engine applies indexed legal action
```

`strategy_sets.py` now owns reusable rev0023 populations:

```text
mlp_ranker_probe_bundles(...)
mulligan_policy_gate_bundles(...)
```

This prevents new scripts from hand-copying strategy panels.

## Audit additions

The cube audit now checks:

```text
MLP model JSON exists and matches the public feature count
MLP agent can choose a legal action
MLP payoff summary passed promotion/stat/C++ trace gates
mulligan policy gate passed promotion/stat/C++ trace gates
mulligan gate saw all three policies
new docs/scripts/tests exist
```

## Known caveat

The MLP model is trained on weak public/code/ranker behavior. It is an infrastructure probe, not proof that learned policies are strong.

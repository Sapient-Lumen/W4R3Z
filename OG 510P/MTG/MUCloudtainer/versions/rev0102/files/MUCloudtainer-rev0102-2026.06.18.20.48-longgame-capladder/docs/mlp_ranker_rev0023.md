# rev0023 — tiny MLP action-ranker

rev0023 adds the first non-linear public action-ranker.

It keeps the same boundary as the linear ranker:

```text
DecisionFrame.observation + legal action candidate -> score
```

The model receives no `GameState`, no opponent hand, and no hidden library. It is a one-hidden-layer MLP exported to JSON, not a pickle. The JSON contains feature names, first-layer weights, hidden bias, output weights, output bias, activation, and training summary.

## Why this before heavier RL

The linear ranker proved the supervised-action interface works, but it is too shallow to model simple interactions such as:

```text
Force is worse at low life unless the target is a game-winning threat.
Jace +2 choices depend on whose top card is being viewed.
Counterspell matters differently when the opponent is tapped low.
```

The MLP is a tiny non-linear probe. It is not expected to become a champion. Its job is to test whether our feature/action interface supports non-linear listwise ranking before PPO/CFR/search starts consuming more rollout budget.

## Policy names

New public-safe agents:

```text
mlp_ranker_rev0023
mlp_ranker_blend_threat_rev0023
mlp_ranker_blend_counter_rev0023
mlp_ranker_blend_patient_rev0023
```

Blend agents add a small readable-profile prior to the MLP score. This is deliberately auditable and weaker than a full learned policy.

## Generated artifacts

```text
data/rev0023_mlp_ranker_training_dataset.csv
data/rev0023_mlp_ranker_model.json
data/rev0023_mlp_ranker_feature_importance.csv
data/rev0023_mlp_ranker_games.csv
data/rev0023_mlp_ranker_aggregate.csv
data/rev0023_mlp_ranker_standings.csv
data/rev0023_mlp_ranker_pairwise.csv
data/rev0023_mlp_ranker_stat_standings.csv
data/rev0023_mlp_ranker_replay_traces.jsonl
data/rev0023_mlp_ranker_cpp_trace_summary.json
data/rev0023_mlp_ranker_summary.json
```

## Caveat

This is imitation of existing public/code/ranker behavior. It can only learn the distribution it sees. Good supervised metrics do not imply strategic strength; the promotion/stat/replay/C++ gates are still required before any result is treated as a population fact.

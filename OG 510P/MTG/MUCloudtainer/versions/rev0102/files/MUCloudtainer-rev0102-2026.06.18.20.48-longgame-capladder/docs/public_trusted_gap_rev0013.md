# rev0013 public-vs-trusted gap diagnostic

Older scripted agents used this interface:

```text
choose_action(GameState, rng) -> Action
```

Even if those agents usually called `state.observation(player)`, receiving the full `GameState` is the wrong contract for learning methods. rev0013 adds a diagnostic script:

```text
scripts/run_rev0013_public_trusted_gap.py
```

It compares old trusted-state agents against public `DecisionFrame` agents over the same deck/life/seed grid.

## Generated files

```text
data/rev0013_public_trusted_gap.csv
data/rev0013_public_trusted_gap_summary.csv
data/rev0013_public_trusted_gap_summary.json
```

## Important interpretation

The gap table is a diagnostic, not proof of leakage.

```text
heuristic_exact
  old trusted HeuristicAgent scorer vs public DecisionFrame wrapper around the same scorer
  expected: exact agreement

heuristic_profile / counter_happy_profile / threat_rush_profile
  old trusted profiles vs newer public profile implementations
  expected: differences because the scorers are not byte-for-byte identical
```

The rev0013 result is reassuring:

```text
heuristic_exact same_winner_rate = 1.0
heuristic_exact mean_abs_decision_delta = 0.0
```

That says the public DecisionFrame path can reproduce an old scorer when the scorer is actually the same. The profile gaps mostly say the public profile code is different, not that hidden state is being used.

## Why keep the diagnostic?

Future method comparisons can accidentally mix these interfaces:

```text
trusted-state scripted baselines
public-frame code policies
public-frame neural policies
external-seat gametable choices
search agents with sampled hidden states
```

The gap diagnostic is a cheap way to catch suspicious divergence before treating results as MUC theory.

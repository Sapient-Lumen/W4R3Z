# rev0009 Experiment Matrix Additions

## New experimental axis: agent interface

```text
trusted_state_agent
public_decision_frame_agent
slot_env_agent
```

Only `public_decision_frame_agent` and `slot_env_agent` are suitable for future learned methods. `trusted_state_agent` is for scripted baselines and debugging.

## New experimental axis: scoring convention

```text
draw_half_score
terminal_win_rate
truncation_rate
mean_decisions
```

Do not collapse these too early. A strategy with high draw-half score and high truncation rate may be exploiting the cutoff rather than winning.

## New experimental axis: mulligan as bundle component

```text
keep_always
land_band
land_band_business
learned_mulligan_policy_later
```

rev0009 adds a smoke payoff table where mulligan policy is part of the strategy id.

## Near-term build order

1. Keep using public DecisionFrame for learned/search agents.
2. Add a simple evolutionary constructor over deck + mulligan policy + heuristic pilot.
3. Add confidence intervals / repeated reps to payoff tables.
4. Add closed-decklist vs open-decklist config before any belief-state search.
5. Only then add neural policy/value experiments.

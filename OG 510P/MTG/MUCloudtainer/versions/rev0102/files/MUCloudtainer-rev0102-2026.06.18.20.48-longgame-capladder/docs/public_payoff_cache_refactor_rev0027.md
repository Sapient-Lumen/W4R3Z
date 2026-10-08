# rev0027 public payoff cache refactor

rev0027 refactors `src/muc5/public_payoff.py` so bulk payoff loops cache both gameplay agents and mulligan agents by name/policy.

Before rev0027, `build_public_payoff_rows(...)` cached public gameplay agents but still rebuilt mulligan agents inside each game row.  That was acceptable for deterministic rule mulligans, but it becomes wasteful once mulligan policies can load JSON-backed models:

```text
mulligan_ranker_rev0024
mulligan_outcome_ranker_rev0027
```

The new path lets `play_public_strategy_pair_row(...)` accept optional prebuilt mulligan agents:

```python
play_public_strategy_pair_row(
    left,
    right,
    ...,
    agent0=cached_agent(left.agent_name),
    agent1=cached_agent(right.agent_name),
    mulligan_agent0=cached_mulligan(left.mulligan_policy),
    mulligan_agent1=cached_mulligan(right.mulligan_policy),
)
```

This is an optimization/refactor only.  The fairness boundary is unchanged:

```text
mulligan agent receives MulliganObservation + legal mulligan actions
gameplay agent receives DecisionFrame observation + legal gameplay actions
neither receives GameState as a policy input
```

The cache is deliberately local to the payoff builder.  Scripts that need fresh policy instances can still call the factories directly.

# rev0022 performance/refactor note

rev0021 showed that subprocess-per-action C++ checks are a trap and batch calls are required. rev0022 keeps that policy and applies a smaller Python-side optimization:

```text
public payoff loops now cache public agent objects by agent name
```

Before rev0022, `build_public_payoff_rows(...)` constructed agents inside every game row. That was acceptable for hand-coded agents but wasteful for JSON-backed rankers because the frozen model could be reloaded repeatedly.

The refactor changes `play_public_strategy_pair_row(...)` to accept optional prebuilt public agents:

```python
play_public_strategy_pair_row(..., agent0=..., agent1=...)
```

`build_public_payoff_rows(...)` now creates an agent cache and reuses those objects for the whole payoff table.

## Fairness boundary

This is safe because public agents are stateless over games except for the RNG passed into `choose_action_index`. Reusing the object does not give it persistent hidden memory. The gameplay contract remains:

```text
agent receives DecisionFrame only
agent chooses legal action index
engine applies that exact legal action
```

If future agents become stateful across matches, they must declare that explicitly and should not use the shared payoff cache path.

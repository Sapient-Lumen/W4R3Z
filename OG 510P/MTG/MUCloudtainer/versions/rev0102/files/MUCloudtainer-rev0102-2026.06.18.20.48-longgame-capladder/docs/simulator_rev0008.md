# rev0008 simulator changes

rev0008 adds two simulator-facing improvements without expanding the card pool or changing MUC-5 rules.

## Trusted application path

`apply_action` now has a validation flag:

```python
apply_action(state, action, rng, validate=True)
```

Default behavior is unchanged: external callers get legality validation.

Hot loops can call:

```python
apply_action(state, action, rng, validate=False)
```

This is safe only when the chosen action came from `legal_actions(state)` for that exact state. `play_agent_game` and `MUC5SlotEnv.step` now use this path after slot validation / agent legal-action choice.

## Log suppression

`GameState` now includes:

```python
record_log: bool = True
```

and `start_game` accepts:

```python
record_log=False
```

Payoff and profiling scripts use `record_log=False`; gametable/debug paths should keep logs on.

## No gameplay-rule changes intended

rev0008 is a plumbing/performance/payoff revision. It is not supposed to alter:

```text
five-card pool
life-total dial
London mulligan logic
stack/counter rules
Jace behavior
Overlord behavior
combat behavior
hidden-information observations
```

The new tests compare trusted/safe application on an opening action and run both validation modes through a short game.

## New scripts

```text
scripts/run_rev0008_payoff_table.py
scripts/profile_simulator_rev0008.py
```

## New tests

```text
tests/test_rev0008_payoff_perf.py
```

## Next simulator priorities

1. Add precomputed/legal-action-list handoff to built-in agents.
2. Reduce `observation()` dictionary allocation in non-neural heuristic tournaments.
3. Add a replay/log mode that can reconstruct selected games without logging every training game.
4. Add process-parallel payoff generation after single-process hot-loop cleanup.

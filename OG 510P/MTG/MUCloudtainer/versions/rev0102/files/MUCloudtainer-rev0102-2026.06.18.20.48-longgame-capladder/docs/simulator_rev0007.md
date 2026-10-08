# rev0007 simulator note

rev0007 does not expand the five-card rules surface. It adds a table wrapper and a couple of deliberately different sparring agents.

## New simulator-facing object

```python
MUC5GameTable(
    deck0,
    deck1,
    seats=(SeatSpec.external(), SeatSpec.from_agent_name("threat_rush")),
    seed=77,
    starting_life=20,
    mulligan_policy="land_band",
).start()
```

The table calls the existing engine:

```text
start_game
legal_actions
apply_action
```

So the table cannot choose illegal moves. It only serializes the legal-action surface into a form an outside controller can use.

## New sparring baselines

```text
CounterHappyAgent
ThreatRushAgent
make_agent(name)
```

`CounterHappyAgent` over-values fighting on the stack. `ThreatRushAgent` over-values committing Jace/Overlord and attacking. These are not strategic claims; they create opponent variety for the table and future payoff matrices.

## Optimization / simplification retained

The table still uses legal macro-actions, not a global action catalog. This remains important because MUC-5 has state-dependent branching: a normal main phase may have only PASS/PLAY_ISLAND, while a response frame with Force pitch options may have many legal actions.

The table also supports resumability through pickle:

```text
save_table(table, path)
load_table(path)
```

This is intentionally pragmatic. The stable exchange object for future LLM controllers is `TableSnapshot.to_dict()`, not the pickle itself.


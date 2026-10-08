# rev0007 experiment-matrix additions

## New factor: controller type

```text
controller_type ∈ {
  random_agent,
  heuristic_agent,
  counter_happy_agent,
  threat_rush_agent,
  external_table_controller,
  future_learned_policy,
  future_code_policy
}
```

## New artifact type: table transcript

Each external-table session can produce:

```text
initial snapshot
legal action menus
external action choices
agent auto-actions
terminal result
```

This becomes useful supervised/evaluation data:

```text
observation + legal_actions + chosen_action + result
```

## Next payoff-table target

The next useful tournament object is not just agent-vs-agent. It is:

```text
strategy = decklist + life construction context + mulligan policy + pilot/controller
```

A payoff row should include:

```text
strategy0_id
strategy1_id
starting_life
known_or_unknown_life_construction_context
game_seed
starting_player
winner
decisions
terminal_reason
```

The table layer gives us a way to insert external/manual/LLM-derived strategies into the same population.


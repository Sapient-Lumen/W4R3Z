# rev0012 public profile agents

rev0012 adds `src/muc5/public_agents.py`, which gives the payoff and oracle scripts named policy personalities that only consume `DecisionFrame` objects.

This matters because the older trusted-state scripted agents receive the omniscient `GameState`. That is useful for debugging, but it is the wrong boundary for anything we might compare against learned methods.

The new public agents see only:

```text
frame.observation
frame.legal_actions
```

They do not see:

```text
opponent hand
opponent library order
future draws
hidden pending-choice data
```

## Current profiles

```text
public_heuristic_rev0012
public_counter_happy_rev0012
public_threat_rush_rev0012
public_patient_rev0012
public_random_rev0009
```

The profiles intentionally remain simple. They are sparring bots and payoff-table plumbing, not claims of strong MUC play.

## Refactor note

Some scoring logic duplicates the trusted `HeuristicAgent` rather than importing its whole state-facing interface. That duplication is acceptable for now because it keeps the public-agent boundary obvious. Future refactors should extract a pure `score(observation, action)` utility shared by trusted and public agents.

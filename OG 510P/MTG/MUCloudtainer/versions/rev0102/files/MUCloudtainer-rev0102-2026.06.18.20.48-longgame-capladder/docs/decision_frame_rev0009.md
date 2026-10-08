# rev0009 DecisionFrame Interface

rev0008 added a fast path:

```python
apply_action(state, action, rng, validate=False)
```

That avoids recomputing legal actions after a trusted agent already chose from `legal_actions(state)`. The concern is correct: this is fast, but it can become unsafe if agents are passed omniscient state or if stale actions are reused.

rev0009 adds:

```text
src/muc5/decision.py
```

Core objects:

```python
DecisionFrame(
    player,
    state_revision,
    observation,
    legal_actions,
)

build_decision_frame(state)
apply_decision_index(state, frame, action_index, rng)
```

## Contract

The referee creates one DecisionFrame for the current actor. The policy sees the observation and legal action instances. The policy returns an index. The engine applies that exact indexed action without recomputing legality.

Safety checks:

- frame revision must match state revision
- frame player must match current actor
- action index must be in range

Speed property:

- legal actions are enumerated once for the decision frame
- `apply_action(..., validate=False)` avoids the second enumeration

Fairness property:

- the policy does not need to receive `GameState`
- the policy cannot inspect hidden hands/libraries unless somebody passes them separately

## Public baseline agents

rev0009 adds:

```text
PublicRandomAgent
PublicHeuristicAgent
play_public_agent_game(...)
```

The public heuristic reuses the old heuristic scoring function but feeds it only:

```text
frame.observation
one legal action at a time
```

That gives us a migration path: old trusted agents remain for compatibility, while learned/search agents should use public DecisionFrames.

## Why not use a cryptographic state hash?

A hash of the full state would include hidden information. Even if not directly reversible, it is an unnecessary side channel. The current guard is a plain integer `GameState.revision` incremented after every macro-action. It is enough to reject stale frames without encoding hidden state.

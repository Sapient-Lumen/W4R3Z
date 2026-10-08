# rev0003 RL/search interface

The project has two competing needs:

1. The referee must emit exact legal macro-actions.
2. Learning algorithms often want a fixed-size action surface.

A global Magic action catalog would be premature because the action universe includes dynamic choices like:

```text
ForceOfWill(pitch_card=JaceTheMindSculptor, target_id=7)
JaceBrainstormPutback(first=Island, second=ForceOfWill)
ATTACK(to_player=2, to_jace=1)
BLOCK(block_player_attackers=1, block_jace_attackers=0)
```

rev0003 uses a simpler bridge: **slot actions**.

## SlotObservation

`MUC5SlotEnv.observe()` returns:

```text
player
raw hidden-information observation
feature_vector
feature_names
action_mask
action_strings
```

`action_mask` has fixed length, default 256. The first N slots correspond to the current legal macro-actions; the rest are padding.

```text
action_mask = [1, 1, 1, 0, 0, 0, ...]
action_strings = [
  "PASS",
  "PLAY_ISLAND",
  "CAST(card=JaceTheMindSculptor)",
]
```

The model chooses a slot. The environment maps the slot back to the exact `Action` object and applies it.

## Why this is useful now

This preserves the core legal-move contract:

```text
referee enumerates legal choices
agent ranks only those choices
illegal moves never enter the policy target
```

It also avoids burning time on a brittle global action ID scheme before the simulator stabilizes.

## Why this may not be the final interface

For off-the-shelf PPO/DQN, slot `3` does not always mean the same semantic action. That can be awkward for simple fixed-logit policies.

Future options:

```text
1. Keep slot actions and train pointer/listwise policies over legal action embeddings.
2. Build a global semantic action catalog after observing real high-branching states.
3. Use search/CFR methods over dynamic legal lists directly.
4. Build a PettingZoo adapter around the stable slot env.
```

## Observation features

`features.py` creates a stable numeric baseline vector from:

```text
frame / main phase
turn number
own hand counts
own library count
public self state
public opponent state
stack counts
pending choice kind
```

This is not the final neural representation. It is a useful baseline for:

```text
heuristic agents
tabular sanity checks
small MLP pilots
arena logging
feature importance / audit work
```

## rev0003 action-mask invariant

The audit checks:

```text
len(action_mask) == max_action_slots
sum(action_mask) == len(action_strings)
len(feature_vector) == len(feature_names)
```

If a legal frame ever exceeds the slot budget, the env raises loudly instead of silently truncating.

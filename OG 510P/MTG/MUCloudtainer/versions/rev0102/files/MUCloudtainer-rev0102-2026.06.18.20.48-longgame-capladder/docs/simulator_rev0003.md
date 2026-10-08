# Simulator rev0003 notes

rev0003 keeps the five-card world exact-to-card, but continues compressing the engine boundary so learning code does not have to reason about full Magic machinery.

## Rules/kernel changes

### Postcombat main phase added

rev0002 effectively had one main phase: pass main -> attack/end. That was too compressed for Overlord of the Floodpits because attacking draws two and discards one, and those cards can matter before the turn ends.

rev0003 adds:

```text
MAIN(precombat)
  PASS -> ATTACK
ATTACK
  PASS / attack choices -> MAIN(postcombat)
MAIN(postcombat)
  PASS -> end step / cleanup / next turn
```

This preserves the legal possibility of casting Jace or Overlord after combat, while avoiding a full phase/priority UI.

### Cleanup / impending audit fix

rev0002 could process `_end_turn()` twice when cleanup discard was required. That meant impending counters could tick twice in the same turn if the active player had to discard at cleanup.

rev0003 adds `_advance_to_next_turn()` and makes cleanup discard resume directly into the next turn, without re-running end-step impending logic.

### Force of Will at one life

The legal-action generator now permits Force of Will's alternate cost at exactly 1 life. The action is legal; paying the cost drops the player to 0 life and the state-based check immediately makes them lose. That matters because the project is about legal move generation, not strategic pruning.

### Jace legend rule / fresh-object audit

If a player has already activated an old Jace and resolves a new Jace, choosing to keep the new one now resets `jace_used_this_turn` to `False`. Choosing to keep the old one restores the old used flag.

This is important for the no-four-of deck-construction world: extra Jaces are not merely redundant cards; they can become fresh planeswalker objects.

## New runnable pieces

```text
src/muc5/features.py       stable numeric observation feature encoder
src/muc5/env.py            MUC5SlotEnv, a small AEC-like slot-action wrapper
src/muc5/agents.py         RandomAgent, HeuristicAgent, play_agent_game
scripts/run_tiny_arena.py  128-game seed-deck heuristic arena
```

## Current simulator status

The engine now supports:

```text
opening hands
first-player draw skip
draw step / decking
precombat main
postcombat main
one Island per turn
auto-paying anonymous Islands
Jace casting / activation / legend choice
Overlord full-cost and impending casting
Overlord enter and attack draw-two-discard-one
Counterspell and Force counter wars
Force mana or pitch payment
Force pitch identity
basic Overlord combat
Jace loyalty damage and death
cleanup discard
hidden observation object
legal macro-action enumeration
random and heuristic trajectories
```

Still intentionally missing or compressed:

```text
mulligans
sideboarding
full Magic phase/priority UI
full target system
full replacement/prevention effects
full type/layer system
explicit individual Island IDs
post-resolution priority choices that do not matter in this five-card pool
```

## Strategic caveat

The heuristic arena data is plumbing data. It confirms that games run, logs terminate, and seed decks can be compared under a named policy. It is not yet evidence about optimal construction.

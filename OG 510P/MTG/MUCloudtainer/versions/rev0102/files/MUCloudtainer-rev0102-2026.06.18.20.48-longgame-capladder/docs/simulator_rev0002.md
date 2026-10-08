# Simulator rev0002 Notes

rev0002 introduces `src/muc5/engine.py`, a stateful referee prototype.

## Main dataclasses

```text
PlayerState
  life
  library
  hand
  graveyard
  exile
  islands_untapped / islands_tapped
  jace_loyalty / jace_used_this_turn
  overlord_ready / overlord_sick / overlord_tapped
  impending_4 / impending_3 / impending_2 / impending_1

StackSpell
  spell_id
  controller
  card
  mode
  params

GameState
  players
  active_player
  frame
  stack
  pending_choice
  pending_combat
  turn_number
  winner / loss_reason
  log
```

The top of each library is `library[-1]`. Hands and graveyards use `Counter[str]` because card identity is only five symbols.

## Decision frames

The simulator does not expose every priority pass. It exposes frames where the acting player has a meaningful legal choice:

```text
MAIN
RESPONSE
ATTACK
BLOCK
CHOICE
GAME_OVER
```

This is the intended bridge toward an AEC-style turn-based learning API.

## Implemented spell/effect behavior

Implemented in rev0002:

- draw from library and lose on draw from empty library;
- play Island;
- auto-pay Islands for mana costs;
- cast Counterspell;
- cast Force of Will via mana or pitch cost;
- counter spells on the stack;
- cast Jace;
- Jace +2, 0, -1, and -12 frames/effects;
- Jace legend replacement choice;
- cast Overlord full-cost or impending;
- Overlord enter/attack draw-two-discard-one choice;
- impending counters tick down at that controller's end step;
- basic Overlord combat against player or Jace;
- cleanup discard down to max hand size;
- random legal game trajectories.

## Random game smoke

`run_smoke.py` starts a seed mirror and then calls:

```python
play_random_game(seed_deck, seed_deck, seed=12, max_decisions=300)
```

The point is not strategic quality. Random play will make absurd decisions. The point is to exercise legal-action generation and state transitions until a terminal state or decision cap.

## Why this is still useful

A bad random pilot can still find engine crashes, illegal action leaks, and missing choice frames. That makes it the right first audit companion before a heuristic bot or ML policy exists.

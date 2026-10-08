# rev0028 pregame-state refactor

rev0028 adds an explicit helper:

```python
start_game_from_pregame_state(...)
```

It creates a normal `GameState` from already-resolved post-mulligan private states:

```text
player 0 remaining library
player 0 kept hand
player 0 mulligans taken
player 1 remaining library
player 1 kept hand
player 1 mulligans taken
starting player
starting life
```

## Why this exists

`start_game(...)` is the normal tournament constructor.  It shuffles decks, runs mulligans, and then starts the game.  That is correct for ordinary play, but it is not ideal for counterfactual mulligan probes because one branch can consume extra random numbers during player 0's mulligan process before player 1's pregame state is generated.

The counterfactual probe needs:

```text
same opponent opening hand in both branches
same opponent library in both branches
same first-seven-card look for player 0
same transition randomness after the branch begins
```

So rev0028 separates pregame branch construction from gameplay start.

## Safety contract

The helper is a diagnostic/research constructor, not the default tournament path.

It copies all supplied hands and libraries, records starting deck counts, applies normal first-turn draw-skip semantics, and then returns to the same public DecisionFrame gameplay loop used elsewhere.

The helper does not give agents any extra information.  Gameplay policies still receive only public `DecisionFrame` observations and legal actions.

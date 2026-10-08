# rev0006 simulator notes

## New pregame path

`start_game` now accepts:

```python
mulligan_agents=(agent0, agent1)
```

Each agent must implement:

```python
choose_mulligan_action(obs, legal, rng) -> Action
```

The engine records:

```text
state.mulligan_log
state.mulligan_decision_log
```

`mulligan_log` is one summary row per player. `mulligan_decision_log` records the explicit keep/take/bottom actions.

## Compatibility

Existing calls still work:

```python
start_game(deck0, deck1)
start_game(deck0, deck1, mulligan_policy="land_band")
start_game(deck0, deck1, mulligan_policies=("keep_always", "land_band"))
```

The new path is:

```python
from src.muc5.mulligan import RuleMulliganAgent

agent = RuleMulliganAgent("land_band")
state = start_game(deck0, deck1, mulligan_agents=(agent, agent))
```

Do not pass both `mulligan_agents` and `mulligan_policy`/`mulligan_policies`.

## Why not full pregame AEC yet?

A full multi-agent pregame environment would require alternating declarations and simultaneous mulligan execution. For rev0006, the simpler isolated opening-hand resolver is enough:

```text
player 0 resolves own mulligan process
player 1 resolves own mulligan process
public mulligan counts enter gameplay observations
```

This is not trying to model pregame bluffing. It is trying to make keep/bottom policy learnable.

## Invariants

Card conservation still applies after mulligans. Bottomed cards go to the bottom of the library as actual card IDs, not synthetic markers.

## Known simplification

The opponent does not get a decision during your mulligan process. That is acceptable for MUC-5 right now because no card in the five-card universe interacts with pregame actions, and gameplay observations expose public mulligan counts.

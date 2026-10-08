# rev0007 gametable: external-seat protocol

rev0007 adds a small **assistant-facing gametable**. The goal is not a polished human UI. The goal is a table protocol that lets an outside chooser, including ChatGPT in a later turn, sit in one seat while named agents play the other seats automatically.

The core contract is unchanged:

```text
MUC-5 referee state
  -> hidden-information observation
  -> numbered legal macro-action menu
  -> external chooser returns an action index
  -> table applies action and auto-plays named agents until external is to act again
```

This is the gameplay analogue of the rev0006 mulligan-agency work. The referee owns legality. The outside chooser owns judgment.

## Files

```text
src/muc5/gametable.py          # MUC5GameTable, SeatSpec, snapshot/render/save/load
scripts/gametable_cli.py       # resumable command-line table protocol
tests/test_rev0007_gametable.py
```

Data examples:

```text
data/rev0007_gametable_initial_frame.md
data/rev0007_gametable_initial_snapshot.json
data/rev0007_gametable_after_action1.md
data/rev0007_gametable_after_action1_snapshot.json
```

## Quick use

List available seed decks:

```bash
python scripts/gametable_cli.py list-decks
```

List seats/agents:

```bash
python scripts/gametable_cli.py list-agents
```

Start a saved table with player 0 external and player 1 as a threat-rush agent:

```bash
python scripts/gametable_cli.py new \
  --deck0 forty_force_jace_pressure \
  --deck1 sixty_overlord_heavy \
  --seat0 external \
  --seat1 threat_rush \
  --life 20 \
  --mulligan-policy land_band \
  --seed 77 \
  --save /tmp/muc5_table.pkl
```

Take legal action slot 1 and resume until the next external decision:

```bash
python scripts/gametable_cli.py act \
  --load /tmp/muc5_table.pkl \
  --action 1
```

Emit a JSON snapshot instead of Markdown:

```bash
python scripts/gametable_cli.py snapshot \
  --load /tmp/muc5_table.pkl
```

## Agent names

```text
random
heuristic
counter_happy
threat_rush
external
```

`counter_happy` and `threat_rush` are rev0007 sparring baselines. They are intentionally crude. Their purpose is diversity, not expert play.

## What the table hides

By default the render shows:

```text
own hand
public battlefield / graveyard / exile counts
opponent hand count
opponent library count
stack
pending choice
legal actions
transcript tail
```

It does **not** show the opponent's hidden hand or library. A debug `--reveal` flag exists for engine audits, but it should not be used for normal play/evaluation.

## Known limitation

External seats do not yet get interactive mulligan menus. The gametable starts after London mulligans have been resolved through an explicit `RuleMulliganAgent`, so mulligan decisions are logged and auditable but not yet externally chosen in the table loop. This is the next obvious pregame UI extension.


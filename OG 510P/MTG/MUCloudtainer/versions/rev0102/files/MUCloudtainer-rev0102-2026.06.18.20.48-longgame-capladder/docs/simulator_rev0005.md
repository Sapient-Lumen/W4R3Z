# rev0005 Simulator Notes

## Added

```text
src/muc5/mulligan.py
src/muc5/invariants.py
```

The simulator now supports an optional London-mulligan baseline before the first turn. Existing no-mulligan behavior is preserved when no policy is supplied.

New public/player metadata:

```text
PlayerState.mulligans_taken
GameState.mulligan_log
GameState.starting_deck_counts
```

New feature columns:

```text
self_mulligans_taken
opp_mulligans_taken
```

## Referee invariant

`src/muc5/invariants.py` counts actual cards across:

```text
library
hand
graveyard
exile
battlefield Islands
battlefield Jace
Overlord creature/impending states
stack spells
legend-rule limbo
pending combat attackers
```

and compares them against each player's starting deck counts.

This audit found and drove a simulator fix: Jace's ultimate now moves the actual cards from the target player's library to exile rather than incrementing a synthetic placeholder counter. That makes card conservation checkable.

## Current simplifications that remain intentional

```text
Only five card IDs exist.
Only actual relevant phases are exposed.
Only Counterspell/Force create response windows.
Islands are anonymous mana sources.
Overlords are aggregated by status.
Jace legend choice is exposed as a small pending-choice frame.
Combat is exact for identical 5/3 flyers, not a generic creature engine.
```

## Current non-goals

```text
No generic Magic card parser.
No generic continuous-effect/layer system.
No full priority UI when no counterspell response is possible.
No learned mulligan policy yet.
No strategic claims from heuristic data yet.
```

## New runnable commands

```bash
python scripts/run_mulligan_probe.py
python scripts/audit_action_space.py
python scripts/audit_cube.py
```

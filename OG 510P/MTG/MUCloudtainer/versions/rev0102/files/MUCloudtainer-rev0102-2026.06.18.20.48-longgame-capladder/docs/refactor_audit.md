# Refactor and Audit Notes

rev0002 includes one deliberate refactor and one audit pass.

## Refactor: centralized card specs

rev0001 scattered card constants through the deck space and legal-kernel scaffold. rev0002 adds:

```text
src/muc5/cards.py
```

This module now owns:

```text
CARD_ORDER
BLUE_NONLANDS
THREATS
INTERACTION
ManaCost
CardSpec
CARD_SPECS
Jace constants
Overlord constants
life/hand/deck-size constants
```

`deckspace.py`, `rules_kernel.py`, `probability.py`, and `engine.py` now import from `cards.py` instead of redefining card symbols.

## Audit script

`scripts/audit_cube.py` checks:

- card-pool JSON order matches code constants;
- `deck_space_all.csv.gz` has the expected 771,127 rows;
- probe outputs exist;
- `probe_rankings_top100.csv` has 100 rows;
- probe ranking is sorted descending;
- seed probe score remains stable.

Audit output is written to:

```text
data/rev0002_audit.json
```

## Current audit result

At rev0002 creation, all audit checks passed.

## Why audit this early

The project will eventually compare learning methods, so silent data drift is dangerous. Even small changes to card constants, deck enumeration, or probability probes could invalidate comparisons. The audit gives each revision a basic reproducibility tripwire.

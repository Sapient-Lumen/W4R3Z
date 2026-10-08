# Experiment matrix — rev0057

The next scientific goal is to separate construction, pilot, mulligan, deck-size, and terminal-mechanism effects.

| ID | Question | Minimal design | Gate |
|---|---|---|---|
| E57-A | Is the edge pilot-driven? | Same two deck shells, swap pilots between decks. | terminal-clean, replay, C++ shadow, mechanism table |
| E57-B | Is the edge deck-driven? | Same pilot on both shells where legal; compare shell scores. | same as above |
| E57-C | Is 60-vs-40 endurance the whole story? | Build 40-card counter-wall and 60-card Overlord controls. | report library-out distribution |
| E57-D | Is Jace Brainstorm causing deck exhaustion asymmetry? | no-Jace or low-Jace variants; keep interaction density comparable. | report draw/putback counts and library-out |
| E57-E | Is mulligan policy driving the result? | `keep_always`, `land_band_business`, and outcome-ranker mulligan variants crossed over both shells. | report opening-hand bands and terminal mechanisms |
| E57-F | Does the result survive a new holdout seed family? | rerun only the best explanatory cells with seed-disjoint holdout. | same replication labels, no rescue by prior evidence |

Recommended first batch: E57-A + E57-C, because they most directly test whether the claim is a pilot skill result or a deck-size/endurance artifact.

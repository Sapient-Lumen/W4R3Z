# rev0014 static MAP-Elites seed archive

rev0014 adds a static MAP-Elites-style deck archive:

```text
src/muc5/map_elites.py
scripts/run_rev0014_map_elites_seed.py
data/rev0014_map_elites_archive.csv
data/rev0014_map_elites_summary.json
```

This is **not** a gameplay optimizer. It uses the existing static life/probe deck priors to illuminate diverse deck regions before we spend simulation budget on them.

## Descriptor grid

Each deck is mapped into a cell using:

```text
deck size       40 or 60
land bin        land_light / land_mid / land_heavy
force bin       force_none / force_low / force_high
counter bin     counter_low / counter_mid / counter_wall
threat bin      no_threat / jace_heavy / overlord_heavy / mixed_threats
life bias       life20_lean / life40_lean / life_robust
```

The archive keeps the highest static-quality deck per cell.

## Why this belongs

Pure best-deck search can collapse onto one local optimum. MUC-5 has several interpretable construction axes:

```text
40 vs 60 cards
Force density vs pitch density
Jace lock vs Overlord clock
20-life aggression vs 40-life resilience
mulligan tolerance
```

MAP-Elites is a good fit because it preserves weird but potentially useful niches. A deck that is bad overall may be an important response to one population cluster.

## Current rev0014 output

The rev0014 archive used seed-deck mutations plus random plausible samples and produced a static archive. The summary records cell count, source counts, life-bias cells, and top cells.

## Next version idea

The valuable next step is not to trust the static archive. It is to pick a small number of archive cells and evaluate them under the same public DecisionFrame payoff/statgate pipeline:

```text
archive cell → strategy bundle → promotion gate → statistical gate → population table
```

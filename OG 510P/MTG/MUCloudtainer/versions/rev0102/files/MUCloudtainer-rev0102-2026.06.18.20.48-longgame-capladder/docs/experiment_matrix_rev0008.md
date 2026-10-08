# rev0008 experiment matrix

rev0008 adds the first payoff-table axis. The MUC-5 experiment space now has these active dials:

```text
deck size:          40 or 60
starting life:      20 or 40
constructor info:   known life or unknown/robust life
mulligan policy:    keep_always, land_band, land_band_business, later learned
pilot/controller:   random, heuristic, counter_happy, threat_rush, external, later learned
strategy bundle:    deck + mulligan policy + pilot
```

## Current generated grid

```text
8 strategy bundles
2 life totals
2 starting-player positions
1 rep
= 256 games
```

## Near-term grids worth building

### A. Mulligan policy payoff table

```text
8 seed decks × 3 mulligan policies × 3 pilot families
```

This checks whether mulligan choice is merely consistency polish or a real strategic axis.

### B. Life-known vs life-unknown construction table

```text
known_20 constructors
known_40 constructors
unknown_robust constructors
```

Run each into both 20 and 40 life fields.

### C. Payoff confidence grid

Take a smaller 4-strategy population and run:

```text
4 × 4 × 2 life totals × 2 starts × 32 reps
```

This gives actual confidence intervals before we over-read noisy one-rep payoff tables.

### D. Best-response smoke loop

1. Pick a target mixture from the current population.
2. Sample/evolve candidate deck vectors.
3. Pair each candidate with a pilot family.
4. Add the best-performing bundle to the population.
5. Recompute the table.

This is a toy PSRO-shaped loop.

## ML method comparison hook

The original constructor comparison remains alive:

```text
enumerative
probability-probe shortlist
evolutionary
neural/contextual
hybrid/PSRO
```

rev0008 gives those methods a common evaluation endpoint: payoff rows over strategy bundles.

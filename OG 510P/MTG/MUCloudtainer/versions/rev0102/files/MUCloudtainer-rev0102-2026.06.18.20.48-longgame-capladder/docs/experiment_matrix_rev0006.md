# rev0006 experiment matrix addendum

Mulligans are now promoted to a real axis, but the matrix should stay controlled.

## Current axes

```text
deck size:       40 | 60
starting life:   20 | 40
construction:    known-life | unknown-robust
mulligan policy: keep_always | land_band | land_band_business
pilot:           random | heuristic | future learned/search/evolved
```

## Recommended immediate comparisons

1. **Mulligan policy as evaluation condition**

```text
same deck pairs
same heuristic pilot
20 and 40 life
compare keep_always vs land_band vs land_band_business
```

2. **Constructor robustness**

```text
constructor knows life total
constructor does not know life total
mulligan policy fixed
pilot fixed
```

3. **Pregame-policy learning**

```text
fixed deck
fixed pilot
learn keep/take/bottom policy from game outcomes
```

This can be a contextual bandit before it becomes full RL.

## Avoid for now

```text
Vancouver mulligan
Paris mulligan
arbitrary life totals beyond 20/40
best-of-three sideboarding
public pregame mind games
```

These are all interesting, but they multiply the data requirement before we have one stable learning loop.

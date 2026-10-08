# rev0079 hierarchical population gate

## Risk addressed

rev0078 made the population gate familywise, but the main gate could still be too aggregate-friendly. A global pool can have enough games and a tolerable confidence width while a size or life stratum remains weak, imprecise, or underpowered. That is the classic shape of a Simpson-style promotion bug: the summary row looks clean even though the decision is not robust across scientifically meaningful strata.

rev0079 adds a hierarchical familywise gate. It keeps the global result visible, but it also evaluates mandatory strata before any future policy can be treated as promotable.

## Layers used

```text
global:        mandatory
by_life:       mandatory
by_size:       mandatory
by_size_life:  diagnostic, not mandatory yet because current fine cells are too small
```

All layers use the same broad-pool eligible evidence rule from rev0077: rev0069 and rev0070 complete panels are eligible; adaptive rev0075 challenge rows remain excluded from broad promotion evidence.

## Current result

```text
eligible source summary rows:     72
eligible source game rows:        432
hierarchical gate rows:           12
mandatory rows:                   6
mandatory passed rows:            0
diagnostic passed rows:           0
global familywise LCB:            0.26324362954759206
worst mandatory-layer LCB:        0.0
global optimism over worst layer: 0.26324362954759206
```

Layer breakdown:

```text
global:        1 quarantined_low_security_floor
by_life:       2 quarantined_low_security_floor
by_size:       3 precision_target_not_met
by_size_life:  6 underpowered_min_games
```

The important new information is not that the global pool still fails; that was already known. The important part is that aggregate precision is not enough. Size strata still fail the precision target, and fine size/life strata are underpowered. A future global near-pass should not be promoted unless the mandatory layers also clear.

## Solver hardening

rev0079 also adds exact support-enumeration solving for small rectangular zero-sum games beyond the current two-row surface. A diagnostic 3×3 game solves exactly with value 0.5 and near-zero primal/dual gap, while a 200-iteration fictitious-play fallback still has a visible gap. This keeps future policy-population expansion from silently depending on approximate solver noise when the empirical game is still small enough to solve exactly.

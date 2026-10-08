# rev0005 Action-Space Audit

## Purpose

The MUC-5 engine deliberately emits legal macro-actions instead of a giant global Magic action catalog. rev0005 adds a sampled action-space audit so we can measure whether this simplification is holding.

New script:

```text
scripts/audit_action_space.py
```

Generated artifacts:

```text
data/rev0005_action_space_audit.csv
data/rev0005_action_space_audit_summary.json
```

## Sample design

The audit used:

```text
4 seed decks
20 and 40 starting life
no mulligan and land_band mulligan conditions
heuristic vs heuristic pilots
56 games
max 220 decisions per game
card-conservation invariant checked before/after games
```

## Summary

```text
decision rows:             11,630
max legal action count:    22
mean legal action count:   2.1962
median legal action count: 1
p99 legal action count:    13
```

By frame:

```text
ATTACK:   max 5,  mean 1.1507
MAIN:     max 22, mean 2.5268
RESPONSE: max 22, mean 2.1030
```

By pending choice:

```text
jace_brainstorm_putback: max 22
cleanup_discard:        max 3
discard:                max 5
jace_legend:            max 2
jace_plus2:             max 2
```

## Interpretation

`max_action_slots=64` is enough for the sampled states. The default `MUC5SlotEnv(max_action_slots=256)` remains conservative until stronger policies produce deeper counter wars and larger Brainstorm hands.

The observed maximum of 22 comes mostly from dynamic choice frames:

```text
Jace Brainstorm putback pairs
counter-war response targets x payment/pitch choices
```

This supports the current listwise/slot interface. We do not need a huge fixed global action vocabulary yet.

## Optimization idea

If action counts become large later, the first compression target is Jace Brainstorm. Instead of enumerating ordered card-type pairs from a large hand, we can emit a nested action:

```text
CHOOSE_TWO_TO_PUT_BACK(first_slot, second_slot)
```

For now the explicit enumeration is more transparent and still cheap.

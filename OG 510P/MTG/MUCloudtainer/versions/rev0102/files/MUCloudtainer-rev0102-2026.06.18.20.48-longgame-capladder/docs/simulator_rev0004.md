# rev0004 simulator note

The simulator now supports a starting-life parameter, but it remains a five-card referee rather than a general Magic engine.

## New constructor/gameplay separation

```text
construction phase:
  may know exact starting life, or only know possible life totals

gameplay phase:
  always knows actual life totals
```

This separation is important because it lets us test context-aware construction without making gameplay artificially blind.

## No new legal-action schemas

The life dial adds zero new legal actions. Existing schemas remain:

```text
PASS
PLAY_ISLAND
CAST(...)
ACTIVATE_JACE(...)
ATTACK(...)
BLOCK(...)
CHOOSE_FOR_EFFECT(...)
```

## Why this is an optimization

A tournament scalar is cheaper than adding cards. It stresses valuation and metagame adaptation while preserving the same action grammar, tests, and masks.

## New static-constructor scaffold

The new static constructor prior does not alter the referee. It only ranks deck vectors before a tournament:

```text
DeckVector + ConstructionContext -> candidate deck cohort
```

This keeps the simulator invariant while letting tournaments compare known-life and unknown-life construction regimes.

## Constructor shortlists

The simulator revision also includes a static constructor shortlist layer. This sits outside the game engine:

```text
DeckVector -> exact probability probes -> life-aware static scores -> top-N shortlists
```

The engine remains unaware of whether a deck came from a known-20 constructor, known-40 constructor, or robust-unknown constructor. That separation keeps construction experiments from contaminating game legality.

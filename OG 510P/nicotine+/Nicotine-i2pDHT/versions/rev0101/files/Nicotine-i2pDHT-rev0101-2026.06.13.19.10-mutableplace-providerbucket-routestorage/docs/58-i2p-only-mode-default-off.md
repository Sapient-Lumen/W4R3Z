# I2P-only mode, default off

I2P-only mode is a sovereignty feature, not a default migration strategy.
It should exist early enough that the DHT is designed honestly, but it should be default off until the bootstrap portfolio is healthy.

## Required semantics

When the user selects I2P-only mode:

```text
classic server login: disabled
classic server fallback: disabled
DHT bootstrap: enabled
I2P router: external or managed bundle
contact-card cache: enabled
policy capsules: user-selected
bridge access: optional, never required
```

The client must not silently connect to the old server just because the DHT had a rough start.
A mode that lies is worse than no mode.

## Readiness guess

The prototype uses these readiness signals:

```text
at least N valid signed contact cards
at least G garden/seed-gate cards
at least C entrance channels
freshest card younger than max age
optional: policy capsule not stale
optional: keyspace diversity across buckets
optional: successful recent lookup transcript
```

The numbers are future tuning knobs.
A power user should be able to override them, but the default UI should show why it is or is not confident.

## User-visible state

Good I2P-only UX should say:

```text
DHT only: on
Classic server: off by policy
Entrances: 42 valid, 4 gardens, 5 channels
Lookup health: 3 disjoint paths succeeded recently
Policy: maintainer default + personal blocklist
```

This makes the trade visible.
It also makes contribution visible: if the user becomes a garden, they should see how many cards, queries, and mutable heads they helped refresh.

## Failure behavior

If I2P-only bootstrapping fails, the fallback should be explicit choices:

```text
import invite/contact file
try public seed list
try configured garden seed gate
switch to hybrid/classic mode
inspect diagnostics
```

Not hidden central reconnection.

## Why this belongs in the DHT design phase

If I2P-only mode is an afterthought, the DHT will quietly depend on central entrances.
Designing it now forces the DHT to have seed portfolios, contact-card expiry, garden seed gates, policy freshness, and diagnostics from the beginning.

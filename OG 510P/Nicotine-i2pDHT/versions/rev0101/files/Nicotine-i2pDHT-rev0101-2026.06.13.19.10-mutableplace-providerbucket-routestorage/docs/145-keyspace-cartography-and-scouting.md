# Keyspace cartography and bounded scouting

The risky guess: a node can have plenty of contacts, proofs, and witnesses while still seeing keyspace through a narrow family or introducer lens.

rev0018 adds local XOR-prefix cartography:

```text
RegionObservation(key, family_id, introducer_family, observed_at, counters)
  -> RegionSummary
  -> ScoutAction(region, reason)
  -> CartographyReport
```

## Scout reasons

```text
hole                  no fresh observation for a region
stale                 only expired observations remain
monoculture           one family or introducer dominates a region
low_family_diversity  a region is present but not diverse enough
```

## Design stance

Cartography is not a global map. It is a node's local anti-amnesia map. Its job is to say:

```text
we are seeing too little
we are seeing one family too often
we are trusting one introducer too much
we should scout elsewhere before accepting easy answers
```

This is a route-health tool, not a truth oracle.

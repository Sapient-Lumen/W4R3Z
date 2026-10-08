# Sweep audit and garden budget pressure

Region-ledger sweeps let garden nodes batch provider and mutable-head reannounce work by XOR keyspace region. That is wise, but the plan itself can be poisoned or simply too large.

rev0018 adds `sweepaudit.py`, a local audit surface over a `RegionLedgerReport`.

It checks:

```text
batch count
total weight
maximum batch weight
source-family counts
whether tombstone batches are buried behind ordinary provider work
```

The possible decisions are:

```text
plan_healthy
throttle_weight
quarantine_family_monoculture
prioritize_tombstones
continue_no_batches
```

The local rule:

```text
Garden generosity needs a budget audit before a reprovide sweep becomes a flood.
```

# Mutable head witness pressure

The DHT’s mutability layer should not clone IPNS-style optimism. A signed pointer is not enough. A stale signed pointer, a forked signed pointer, or a pointer with a broken previous link can all be validly signed and still dangerous.

## rev0013 additions

`headwitness.py` introduces:

- `HeadObservation`: a mutable record observed from a source node and path family,
- `HeadWitnessStatement`: a signed garden/witness statement about a head,
- `HeadLookupPolicy`: local thresholds for diversity, stale pressure, previous-link discipline, and witness handling,
- `analyze_mutable_head_lookup`: a local decision procedure.

## Decisions

```text
accept_latest_diverse
accept_latest_with_watch
continue_no_valid_heads
continue_insufficient_diversity
continue_stale_pressure
continue_fork_pressure
continue_prev_mismatch
quarantine_witness_contradiction
```

The accept-with-watch decision is intentionally important. It lets a client move forward when the latest head is path-diverse, while still asking a garden/sentinel layer to preserve evidence and watch for future rollback or fork behavior.

## Hard guess

```text
Mutable-head acceptance should be monotonic locally,
path-diverse operationally,
and witnessable without turning witnesses into authorities.
```

# rev0073 StateCore snapshot replay root

rev0072 could bind an action trace to a `StateCheckpointSeal`, but the caller still had to provide the original in-memory `GameState`. rev0073 closes that immediate replay-root gap with a compact `MTGSim.StateCoreSnapshot.v1` codec and `StateCoreSnapshotParseResult`.

The snapshot is deliberately a **StateCore** artifact, not a journal artifact. It serializes the continuation fields covered by `canonical_state_hash(...)`: card definitions, objects, player zones and mana pools, stack, turn/priority scalars, RNG and ID allocators, pending triggers, prevention shields, and continuous effects. It also carries the source checkpoint seal so a parsed snapshot can be compared against the checkpoint that produced it.

A parsed snapshot reconstructs a `GameState` whose journal is a **trimmed/empty journal**. That is intentional. The codec does not pretend to reconstruct evidence rows, event records, receipt rows, or historical vector capacity. A caller that needs forensic history should keep a separate action trace plus journal/export artifact; a caller that needs a replay root can use this snapshot and then apply a parsed `MTGSim.ActionTrace.v1` trace.

The parser verifies the reconstructed `snapshot.state_hash` before returning success. The replay helper can then reject checkpoint mismatches before mutation and step through the trace with action-hash and pre/post-StateCore-hash checks. This gives the cube a durable cross-file path:

```text
StateCoreSnapshot.v1 + ActionTrace.v1 -> reconstructed replay root -> first-divergence replay check
```

This is still not a complete save-game format. Hidden-information observations, size caps for hostile input, full journal replay, and a compact binary/canonical JSON option remain future work. The important correction is that replay no longer depends on an unshared in-memory checkpoint once a StateCore snapshot is available.

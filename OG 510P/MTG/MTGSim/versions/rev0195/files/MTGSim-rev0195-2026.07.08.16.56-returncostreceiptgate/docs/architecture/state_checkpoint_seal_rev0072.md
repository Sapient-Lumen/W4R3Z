# rev0072 state checkpoint seal

rev0071 made `ActionTraceEntry` rows durable through the `MTGSim.ActionTrace.v1` text codec. The remaining immediate replay risk was starting-state ambiguity: a persisted trace could still be handed to the wrong in-memory checkpoint, i.e. the wrong starting state and only fail once a step hash diverged. rev0072 adds a small checkpoint seal so the engine can reject that mistake before mutation.

## New boundary

`make_state_checkpoint_seal(...)` samples the continuation and journal boundary at the intended replay start. `serialize_state_checkpoint_seal(...)` emits a stable, line-oriented artifact:

```text
MTGSim.StateCheckpointSeal.v1
state_hash=... journal_hash=... journal_entries=... action_receipts=... objects=... players=... stack=... rng=... next_zone_change=... next_event_sequence=... turn=... step=Main1 active=1 priority=1 journal_trimmed=0
```

`parse_state_checkpoint_seal(...)` returns a `StateCheckpointParseResult` with either the parsed seal or a line-indexed failure. The parser rejects malformed tokens, duplicate fields, unknown fields, invalid booleans, invalid steps, and extra data lines.

## Why this matters

`replay_action_trace_from_checkpoint(...)` verifies the seal before delegating to action-trace replay. If the supplied `GameState` is not the sealed checkpoint, the result is `ActionReplayFailureKind::CheckpointHashMismatch`, `attempted == 0`, and no action receipt or journal row is written.

This is useful immediately for agent/search harnesses and future file-level replay commands: a checkpoint seal plus an action trace gives a cheap, durable guard against accidentally comparing traces from different states.

## Not full state deserialization

This is not full state deserialization. The seal does not reconstruct `CardDefinition`, `GameObject`, player zones, pending triggers, continuous effects, or hidden information. It is a compact checkpoint identity contract that makes the current trace replay safer while the larger canonical snapshot format remains future work.

## Next step

The next high-value step is a canonical StateCore snapshot codec that can rebuild a `GameState` from text/binary data, then verify the resulting `StateCore` hash against this same seal before applying `MTGSim.ActionTrace.v1` rows.

## rev0115 schema-seal note

rev0115 keeps historical `MTGSim.StateCheckpointSeal.v1` seals parseable for diagnostics but promotes fresh standalone checkpoint seals to `MTGSim.StateCheckpointSeal.v2` with `checkpoint_schema=`. Replaying from a checkpoint with an unsupported schema now fails as `CheckpointSchemaMismatch` before mutation, while ordinary wrong-state starts still fail as `CheckpointHashMismatch`.

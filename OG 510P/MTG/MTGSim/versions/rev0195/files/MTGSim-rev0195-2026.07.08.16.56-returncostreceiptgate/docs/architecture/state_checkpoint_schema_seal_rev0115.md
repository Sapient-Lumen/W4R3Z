# rev0115 StateCheckpoint schema seal

## Mission seam

rev0114 made replay manifests self-describing with `manifest_schema=`, but the checkpoint seal that binds a trace to its starting StateCore still relied on the `MTGSim.StateCheckpointSeal.v1` header alone. That left checkpoint protocol migration looking like an ordinary checkpoint hash mismatch.

rev0115 promotes the standalone checkpoint seal codec to `MTGSim.StateCheckpointSeal.v2` and adds explicit `checkpoint_schema=` evidence.

## Code boundary

New evidence:

- `kStateCheckpointSealSchemaVersion`
- `StateCheckpointSeal::schema_version`
- `MTGSim.StateCheckpointSeal.v2`
- `checkpoint_schema=` in serialized checkpoint seals
- `ActionReplayFailureKind::CheckpointSchemaMismatch`
- `ActionReplayResult::expected_checkpoint_schema_version`
- `ActionReplayResult::actual_checkpoint_schema_version`

`parse_state_checkpoint_seal(...)` remains able to parse historical `MTGSim.StateCheckpointSeal.v1` artifacts and tags them as schema version `1`. New v2 checkpoint seals must carry exactly one nonzero `checkpoint_schema=` field. `replay_action_trace_from_checkpoint(...)` rejects unsupported checkpoint schemas before comparing StateCore hash, journal hash, or applying trace step one.

## Audit/refactor note

While auditing the checkpoint seam, rev0115 also removes a duplicate read of `priority_player` in `read_checkpoint_snapshot(...)`. The duplicate was harmless because it read the same key into the same field twice, but removing it makes the checkpoint snapshot reader match the writer one-to-one and reduces future review noise.

## Regression

`test_state_checkpoint_seal_schema_drift_rejected_without_mutation` mutates only the checkpoint schema version and confirms replay fails as `CheckpointSchemaMismatch`, with `attempted == 0`, no StateCore mutation, no journal write, and no appended action receipt.

## Non-goal

This cut does not promote `StateCoreSnapshot.v1` to a new snapshot schema. Embedded `source_checkpoint` records are still carried through the snapshot codec as part of the StateCore snapshot surface. The standalone checkpoint text contract is now explicit so future snapshot schema work can migrate with a clear failure class instead of collapsing into generic checkpoint identity drift.

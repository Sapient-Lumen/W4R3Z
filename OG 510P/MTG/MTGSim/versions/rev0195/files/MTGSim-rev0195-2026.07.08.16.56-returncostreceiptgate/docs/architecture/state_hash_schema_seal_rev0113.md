# rev0113 StateCore Hash Schema Seal

## Purpose

`canonical_state_hash(...)` already uses a stable `MTGSim.StateCore.v1` hash-domain label, but before rev0113 that protocol version stayed implicit inside the hash function. Action receipts and serialized traces carried `state_hash_before` and `state_hash_after` without separately stating which StateCore hash schema those values belonged to.

rev0113 makes that boundary explicit with `kStateCoreSchemaVersion` and `state_schema` evidence. The goal is not to change the current hash layout; the goal is to make future hash-schema migration auditable and replay-safe.

## New evidence surface

- `kStateCoreSchemaVersion` is the current StateCore hash schema constant.
- `ActionReceiptRecord::state_schema_version` records the schema used for `state_hash_before` and `state_hash_after`.
- `ActionTrace.v16` serializes this as `state_schema=` beside the state hashes.
- Receipt validation rejects unsupported `state_schema_version` values.
- Replay rejects schema drift through `StateHashSchemaMismatch` before mutating StateCore or the journal.

## Replay semantics

A v16 trace row with `state_schema=1` says: the row's `state_before=` and `state_after=` fields are StateCore hashes using the current StateCore hash protocol. If a future engine expects a different StateCore hash schema, replay can fail with a typed schema diagnostic instead of misclassifying the artifact as ordinary state-content drift.

Older traces remain parseable. v1-v15 rows that contain state hashes default to `kStateCoreSchemaVersion`, preserving historical artifacts while making new artifacts self-describing.

## Audit hook

`test_action_trace_replay_detects_state_hash_schema_drift_without_mutation` mutates the trace's expected state schema and confirms replay returns `StateHashSchemaMismatch` without appending journal entries or changing the StateCore hash. The datacube audit probes the constant, receipt field, `state_schema` text codec, validation error, regression name, and this document so the seam stays visible in future revisions.

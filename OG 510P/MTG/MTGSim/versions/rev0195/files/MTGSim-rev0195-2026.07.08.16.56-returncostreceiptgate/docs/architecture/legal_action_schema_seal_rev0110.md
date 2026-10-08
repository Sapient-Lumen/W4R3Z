# rev0110 — Canonical Action Schema Seal

## Why this seam

The previous proof chain made legal-action pages and APNAP queue locations self-describing: page proofs expose `choice_page_schema=`, and queue-location proofs expose `choice_queue_schema=`. The selected action itself still had the same drift shape rev0109 fixed for queues: the canonical action protocol existed only as the `MTGSim.Action.v1` hash domain and was not visible as typed receipt/trace evidence.

That mattered because `action_hash` is the root selected-action seal used by page-location hashes, queue-location hashes, and replay. If the action encoding ever changes, persisted traces should fail through an explicit action schema check before mutation, not by forcing auditors to infer a protocol mismatch from a compact hash disagreement.

## What changed

rev0110 adds `kLegalActionSchemaVersion` and carries it through the selected-action evidence surface:

- `ActionReceiptRecord::action_schema_version`
- `ActionTraceEntry::expected_action_schema_version`
- `ActionReplayResult` expected/actual action schema diagnostics
- `MTGSim.ActionTrace.v13` field `action_schema=`
- receipt validation error `action_receipt.action_schema_version`

The current `legal_action_hash(...)` remains the canonical `MTGSim.Action.v1` identity for action fields; this cut makes that protocol version visible beside the hash instead of changing the hash value.

## Replay behavior

Replay checks `expected_action_schema_version` before recomputing choice queue/page proofs or applying the action. A nonzero schema that differs from `kLegalActionSchemaVersion` returns `ActionHashMismatch` before StateCore or journal mutation. Diagnostics preserve the expected schema, actual schema, expected hash, and recomputed hash so action schema drift can be distinguished from action payload drift even when the compact hash is otherwise current.

`parse_action_trace(...)` now accepts `MTGSim.ActionTrace.v13` and requires a nonzero `action_schema=` field in v13 rows. Older trace versions remain parseable and default their action schema to the current schema when they carry `action_hash=` evidence.

## Audit/refactor value

The selected-action identity is now aligned with the adjacent proof surfaces:

- page proof: `choice_page_schema=` + page location hash
- APNAP queue proof: `choice_queue_schema=` + queue location hash
- selected action proof: `action_schema=` + action hash

This reduces future upgrade risk by turning action hash protocol drift into first-class typed evidence. The datacube audit now probes the field, parser/serializer surface, receipt validator, architecture note, rule ledger, and the regression `test_action_trace_replay_detects_action_schema_drift_without_mutation`.

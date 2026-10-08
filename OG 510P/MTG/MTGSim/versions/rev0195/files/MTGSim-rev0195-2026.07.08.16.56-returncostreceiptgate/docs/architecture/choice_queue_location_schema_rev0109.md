# rev0109 — APNAP Queue-Location Schema Evidence

## Audit target

rev0107 made APNAP queue entries self-sealing with `ChoiceQueueLocation.v1` and `choice_queue_location_hash`. rev0108 made proof status explicit with checked/found sentinels. The remaining drift seam was protocol visibility: the queue-location proof version existed only inside the hash domain string, while legal-action pages already exposed a first-class schema field.

That meant a persisted trace could prove a queue-location hash and checked/found status without explicitly saying which queue-location proof schema it expected.

## Change

rev0109 adds `kChoiceQueueLocationSchemaVersion` and carries it through the APNAP queue proof surface:

- `ChoiceQueueLocation::schema_version`
- `ActionReceiptRecord::choice_queue_location_schema_version`
- `ActionTraceEntry::expected_choice_queue_location_schema_version`
- `MTGSim.ActionTrace.v12` field `choice_queue_schema=`
- `ActionReplayResult` expected/actual queue-location schema diagnostics

`choice_queue_location_hash(...)` now hashes the explicit schema version as typed proof material. Older `ActionTrace.v10` and `ActionTrace.v11` artifacts remain parseable; they default the expected schema to the current `ChoiceQueueLocation` schema when they carry queue-location hash evidence.

## Replay and validation behavior

Replay recomputes the queue-location proof before mutation. If `choice_queue_schema=` drifts from the current queue-location schema, replay returns `ChoiceQueueHashMismatch` before applying the action, even when the compact queue-location hash otherwise still matches. This keeps schema drift in the same APNAP queue evidence channel as queue hash/index/size and queue-location hash drift.

Receipt validation now rejects legal action receipts with unsupported APNAP queue-location schema versions and recomputes the compact queue-location hash from the schema-bearing typed fields.

## Regression coverage

- `test_action_trace_replay_detects_choice_queue_schema_drift_without_mutation`
- Extended `test_apply_action_records_transition_receipt_hashes`
- Extended `test_action_trace_text_codec_preserves_vector_targets_and_rejects_bad_steps`
- Extended `test_choice_request_queue_metadata_roundtrips_and_guards_replay`

## Mission fit

The mission is trusted transitions. rev0109 makes the APNAP queue proof contract self-describing at the same level as the legal-action page proof contract: state/request/page/queue/action evidence now travels with explicit protocol boundaries, not only with compact hash seals.


## rev0112 naming note

`MTGSim.ActionTrace.v12` through `MTGSim.ActionTrace.v14` serialized the queue-location schema as `choice_queue_schema=`. rev0112 promotes the global APNAP `ChoiceRequestQueue` schema to first-class evidence, so `MTGSim.ActionTrace.v15` reserves `choice_queue_schema=` for the global queue protocol and emits the queue-location schema as `choice_queue_location_schema=`. The parser keeps the v12-v14 legacy meaning for historical artifacts.

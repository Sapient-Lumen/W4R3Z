# rev0112 — APNAP Choice Queue Schema Seal

## Audit target

rev0109 made `ChoiceQueueLocation.v1` explicit, rev0110 made `LegalAction` schema evidence explicit, and rev0111 made the local offered `ChoiceRequest` schema explicit. The upstream APNAP queue still had the same drift shape: the ordered queue protocol existed only inside the `MTGSim.ChoiceRequestQueue.v1` hash domain.

That meant a persisted action receipt or trace could prove a queue hash, queue index, and queue size without explicitly saying which global queue schema produced those values.

## Change

rev0112 adds `kChoiceRequestQueueSchemaVersion` and carries it through the APNAP queue proof surface:

- `ChoiceRequestQueue::schema_version`
- `ActionReceiptRecord::choice_queue_schema_version`
- `ActionTraceEntry::expected_choice_queue_schema_version`
- `MTGSim.ActionTrace.v15` field `choice_queue_schema=`
- `ActionReplayResult` expected/actual choice-queue schema diagnostics

`choice_request_queue_hash(...)` now hashes the explicit schema version as typed proof material. Older traces remain parseable: v12-v14 used `choice_queue_schema=` for queue-location schema, so the parser maps that legacy field to `expected_choice_queue_location_schema_version`; v15 reserves `choice_queue_schema=` for the global queue schema and emits `choice_queue_location_schema=` for the queue-location schema.

## Replay and validation behavior

Replay recomputes the APNAP queue before mutation. If `choice_queue_schema=` schema drift occurs against the current queue schema, replay returns `ChoiceQueueHashMismatch` before applying the action, even when no StateCore or journal mutation has occurred. The diagnostics include expected and actual queue schema versions and preserve the existing queue hash/index/size channel for adjacent drift.

Receipt validation now rejects legal action receipts with unsupported APNAP choice-queue schema versions and folds that version into the canonical action-receipt hash.

## Regression coverage

- `test_action_trace_replay_detects_choice_request_queue_schema_drift_without_mutation`
- Extended `test_apply_action_records_transition_receipt_hashes`
- Extended `test_action_trace_text_codec_preserves_vector_targets_and_rejects_bad_steps`
- Extended `test_choice_request_queue_metadata_roundtrips_and_guards_replay`

## Mission fit

The mission is trusted transitions. rev0112 makes the APNAP queue contract self-describing at the same level as the local request, legal-action page, queue-location proof, and selected action contracts: state/request/page/queue/action evidence now travels with explicit protocol boundaries, not only with compact hash seals.

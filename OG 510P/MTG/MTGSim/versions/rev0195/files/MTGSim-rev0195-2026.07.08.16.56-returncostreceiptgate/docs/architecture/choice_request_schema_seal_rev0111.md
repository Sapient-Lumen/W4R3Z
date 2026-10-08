# rev0111 choice request schema seal

rev0111 makes the offered local choice-request protocol explicit in the same way rev0109 and rev0110 made queue-location and selected-action protocols explicit.

## Problem

`choice_request_hash(...)` already used the stable hash domain `MTGSim.ChoiceRequest.v2`, but that protocol version was only implicit inside the hash recipe. Receipts and persisted traces carried `choice_hash=` and choice metadata, yet they did not state which `ChoiceRequest` schema produced the compact hash.

That left a replay/audit ambiguity: a future change to the offered-choice request contract could fail as a generic choice hash drift, but the artifact would not be able to say whether the selected action changed, the queue changed, or the request schema itself changed.

## Refactor

rev0111 adds:

- `kChoiceRequestSchemaVersion = 2`;
- `ChoiceRequest::schema_version`;
- `ActionReceiptRecord::choice_request_schema_version`;
- `ActionTraceEntry::expected_choice_request_schema_version`;
- `ActionReplayResult` expected/actual choice request schema diagnostics;
- `MTGSim.ActionTrace.v14` with `choice_schema=` beside `choice_hash=`;
- receipt validation code `action_receipt.choice_request_schema_version`;
- `test_action_trace_replay_detects_choice_request_schema_drift_without_mutation`.

The choice-request hash now hashes the visible schema field as data as well as keeping the existing `MTGSim.ChoiceRequest.v2` domain string. This makes the protocol self-describing in receipts/traces and still keeps hash-domain separation.

## Replay behavior

For v14 traces, `parse_action_trace(...)` requires a nonzero `choice_schema=`. Older v1-v13 traces remain parseable; when they carry `choice_hash=` evidence, the parser fills the current `kChoiceRequestSchemaVersion` as the compatibility default.

`replay_action_trace(...)` checks choice request schema before applying the selected action. Choice-request schema drift fails through `ChoiceRequestHashMismatch`, before StateCore or journal mutation, with expected/actual schema diagnostics preserved.

## Why this matters

The mission spine is trusted transitions. A replayable transition should prove not only that an action hash, page proof, and APNAP queue proof match, but also that the local offered choice request was interpreted under the same schema. rev0111 closes that semantic gap without widening the rules surface or changing gameplay behavior.

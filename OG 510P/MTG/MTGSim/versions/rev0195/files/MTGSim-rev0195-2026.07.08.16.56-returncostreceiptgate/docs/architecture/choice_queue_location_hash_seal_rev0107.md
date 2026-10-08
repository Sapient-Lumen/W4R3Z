# rev0107 — APNAP queue-entry hash seal

rev0107 audits the global choice-order boundary that sits immediately before local choice-request and page proof validation. Page proof is now self-sealing, but APNAP queue evidence was still represented by three adjacent fields: `choice_queue_hash`, `choice_queue_index`, and `choice_queue_size`.

That was enough to detect broad queue drift, but it did not give receipts and traces a compact proof that the selected queue entry, the selected local `ChoiceRequest`, and the selected action still belonged together.

## New proof record

`ChoiceQueueLocation.v1` hashes:

- whether the selected queue entry was found;
- the pre-action StateCore hash;
- queue hash, one-based queue index, and queue size;
- selected request kind, chooser, required flag, frontier completion, and generation limit;
- selected request action-set hash and action count;
- selected action hash.

`choice_queue_location_hash(...)` is the canonical compact seal for this tuple.

## Receipt and trace surface

Action receipts now carry `choice_queue_location_hash` beside the existing queue hash/index/size fields. `ActionTrace.v10` serializes the same proof as `choice_queue_location_hash=` and keeps `ActionTrace.v1` through `ActionTrace.v9` parseable.

Applied v10 rows must carry a nonzero queue-location hash. Illegal audit rows still leave it zero, matching the existing pattern for page-proof evidence.

## Replay and validation behavior

Replay still checks broad APNAP queue hash/index/size drift before moving to local request checks. It then checks local choice-request drift before checking the queue-entry seal so old diagnostics keep their specificity: tampering with the request hash remains `ChoiceRequestHashMismatch`, while tampering with the queue-entry seal reports through `ChoiceQueueHashMismatch` before mutation.

Receipt validation recomputes the queue-entry hash from typed receipt fields and rejects missing or stale legal-action queue proof.

The focused regression is `test_action_trace_replay_detects_choice_queue_location_hash_drift_without_mutation`.

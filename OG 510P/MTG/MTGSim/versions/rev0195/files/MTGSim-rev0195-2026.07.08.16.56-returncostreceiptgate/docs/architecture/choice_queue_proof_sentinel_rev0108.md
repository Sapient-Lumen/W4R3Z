# rev0108 — APNAP queue proof sentinel

rev0108 audits the proof boundary introduced in rev0107. A compact `ChoiceQueueLocation.v1` hash is necessary, but not sufficient by itself: without an explicit sentinel, a zero hash can ambiguously mean either “no queue proof was checked” or “queue proof was checked and failed to find the selected entry.”

## Contract

Action receipts now record two queue proof booleans:

- `choice_queue_location_checked`: the transition checked APNAP queue proof for this action.
- `choice_queue_location_found`: the checked proof found the selected action's request in the APNAP queue.

For legal applied actions, both booleans must be true and `choice_queue_location_hash` must be nonzero. For illegal audit rows emitted by `apply_action`, both booleans remain false and the hash remains zero; the illegal row can still carry coarse queue hash/index/size evidence without claiming a checked proof.

## Trace format

`MTGSim.ActionTrace.v11` adds:

- `choice_queue_found=`
- `choice_queue_checked=`

The parser still accepts v1-v10. v10 traces with a nonzero `choice_queue_location_hash=` are interpreted as checked and found for compatibility.

## Replay behavior

Replay rejects applied traces that carry a queue-location hash while eliding `choice_queue_checked`. This catches proof omission before mutation even if the compact hash still matches the current queue. Hash drift, queue-order drift, request drift, and page drift keep their existing diagnostic channels.

## Why it matters

The mission is not just deterministic replay; it is explainable trust in every accepted transition. The queue proof sentinel makes the APNAP boundary explicit enough for agents, fuzzers, and humans to tell absence of proof apart from negative proof.

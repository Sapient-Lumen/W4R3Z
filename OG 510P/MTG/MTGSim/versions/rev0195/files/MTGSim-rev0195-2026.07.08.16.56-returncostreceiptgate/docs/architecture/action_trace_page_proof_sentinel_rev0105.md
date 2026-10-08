# Action Trace Page-Proof Sentinel — rev0106

rev0106 audits the trace/receipt seam immediately after the page context seal.

rev0104 made page evidence rich enough to be portable: schema, hash, counts, StateCore context, and ChoiceRequest context all travel with the selected action. The remaining ambiguity was smaller but important: `choice_page_found=false` could mean either “the page locator was checked and did not find this action” or “no page proof was checked because this was an illegal full-trace audit row.” Those are not the same claim.

## Contract

Action receipts now separate two facts:

- `choice_page_location_found`: a positive located-page claim exists;
- `choice_page_location_checked`: the transition actually performed the page-proof check.

For legal applied actions, both must be true. For illegal attempts exported through `export_action_trace(game, false)`, both remain false so forensic traces can still replay rejected attempts without pretending a page proof exists.

`ActionTraceEntry` carries the same split as `expected_choice_page_location_found` and `expected_choice_page_location_checked`.

## Trace format

`serialize_action_trace(...)` now emits `MTGSim.ActionTrace.v8` and includes:

```text
choice_page_found=1 choice_page_checked=1
```

The parser remains backward-compatible with v1-v7. Older page-location traces map checked status from the older positive-found claim. v8 rejects an applied row that carries page fields but does not mark the page proof checked; this prevents a serialized applied action from silently downgrading its own page proof.

## Replay and validation

Replay now treats page-proof elision on an applied action as `ChoicePageLocationMismatch` before StateCore or Journal mutation. If page proof is checked, replay recomputes `locate_legal_action_page(...)` and compares the existing page schema/hash/count/context/location evidence as before.

Receipt validation now rejects:

- legal receipts without a checked page proof;
- illegal receipts that claim a checked page proof;
- positive page locations that are not marked checked.

The new regression `test_action_trace_replay_rejects_applied_choice_page_proof_elision_without_mutation` proves that an applied trace cannot clear `expected_choice_page_location_checked` and still replay.

## Why this matters

The mission is trusted transitions, not just successful transitions. A replay artifact should distinguish “this action had a verified page proof” from “this row carried no page proof because it was a rejected audit attempt.” rev0106 makes that distinction explicit and machine-checkable without changing the page schema itself.

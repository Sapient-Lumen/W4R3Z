# rev0099 — Action trace page-location proof

rev0098 added `locate_legal_action_page(...)` so a selected legal action could be found in deterministic cursor pages. rev0099 makes that proof durable at the action boundary.

## Problem fixed

A replay trace could already prove that a selected action was legal and whether it came from the offered frontier or direct domain validation. It still could not prove that the action occupied the same deterministic page position that an agent, debugger, or resumable search process would use.

That gap matters most for actions outside the first 128-action bounded frontier. A tail combat declaration might still replay as legal while the page ordering or cursor contract drifted under the caller.

## New durable evidence

`ActionReceiptRecord` now records page-location metadata for legal actions:

- `choice_page_location_found`
- `choice_page_requested_limit`
- `choice_page_effective_limit`
- `choice_page_cursor`
- `choice_action_cursor`
- `choice_page_index`
- `choice_page_next_cursor`
- `choice_page_actions_seen`
- `choice_page_scanned_pages`
- `choice_page_complete`
- `choice_page_hash`

For bounded combat frontiers, the default page proof limit is the published frontier generation limit. This keeps the normal frontier small while proving where directly validated tail actions live in the paged surface.

## Trace format

`serialize_action_trace(...)` emitted `MTGSim.ActionTrace.v3` rows in rev0099. rev0100 upgrades the current serializer to `MTGSim.ActionTrace.v4`; v4 keeps the v2 source-aware fields and the v3 page-location fields and adds `choice_page_hash` evidence:

```text
choice_page_found=1
choice_page_requested=128
choice_page_limit=128
choice_page_cursor=128
choice_action_cursor=255
choice_page_index=127
choice_page_next=256
choice_page_seen=256
choice_page_scanned=2
choice_page_complete=1
```

`parse_action_trace(...)` still accepts v1 and v2. Older traces have wildcarded page-location evidence; v3 requires the complete page-location field group.

## Replay guard

`replay_action_trace(...)` now recomputes `locate_legal_action_page(...)` before applying a traced action when v3 page-location evidence is present. If the current engine derives a different page position, replay returns `ChoicePageLocationMismatch` before StateCore mutation and before replay receipts are appended.

## Tests

- `test_action_trace_replay_detects_choice_page_location_drift_without_mutation` corrupts the traced action cursor for a directly validated eight-attacker tail declaration and verifies that replay fails before mutation.
- `test_truncated_attack_frontier_accepts_direct_legal_declaration_and_replays` now checks that the receipt stores the page location for a legal action beyond the bounded prefix.
- `test_action_trace_text_roundtrip_replays_from_checkpoint` verifies the `ActionTrace.v3` text codec and page-location fields.

## Refactor note

The pass also removed a duplicated choice-request classification call in `choice_request_for_player_with_state_hash(...)`, reducing one source of future drift in the choice-surface construction path.


## rev0100 page hash addendum

`ActionTrace.v4` adds `choice_page_hash` so `ChoicePageLocationMismatch` can also diagnose page-content drift before StateCore mutation. This prevents a trace from proving only that an action was at a cursor/index while ignoring changes in the returned page around that action. Older `ActionTrace.v3` artifacts remain parseable without page-hash claims.

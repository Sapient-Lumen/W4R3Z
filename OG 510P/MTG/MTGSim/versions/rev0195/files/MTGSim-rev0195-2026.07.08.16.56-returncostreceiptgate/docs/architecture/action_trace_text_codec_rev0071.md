# rev0071 action trace text codec

rev0070 made action receipts replay-checkable inside one process. rev0071 removes the next fragile assumption: the trace no longer has to stay as an in-memory `std::vector<ActionTraceEntry>`.

## New boundary

`serialize_action_trace(...)` emits a stable, line-oriented text artifact:

```text
MTGSim.ActionTrace.v1
step=1 kind=pass_priority player=1 object=0 mode=0 ability=0 mana=0 applied=1 action_hash=... state_before=... state_after=... targets=-
```

`parse_action_trace(...)` returns an `ActionTraceParseResult` with either parsed entries or an explicit line-indexed failure. The parser rejects malformed fields, duplicate keys, unknown action/target kinds, invalid booleans, and non-contiguous step numbers before replay mutates a checkpoint.

## Why this matters

This is not full checkpoint serialization, but it is the minimum durable replay seam. A future file-level replay command can now take:

1. a checkpoint snapshot,
2. an action trace text file,
3. the final expected `StateCore` hash,

and stop at the first action that diverges.

## Codec constraints

- The header is versioned as `MTGSim.ActionTrace.v1`.
- `LegalAction::label` is never serialized.
- Multi-target choices use `targets=` with comma-separated `kind:player:object:zone_change_index` entries.
- `targets=-` is the no-target sentinel.
- Zero expected hashes remain wildcards after parsing, matching hand-built trace behavior.

## Remaining gap

The riskiest remaining replay gap is checkpoint serialization. The engine can now persist and parse action intent, but the starting `GameState` still needs a canonical snapshot format before cross-process replay is complete.


## rev0096 v2 compatibility note

`serialize_action_trace(...)` now emits `MTGSim.ActionTrace.v2`. The v2 row keeps the v1 action/hash/checkpoint fields and adds source-aware choice evidence, including `choice_source=`. This records whether the selected action was an `offered_action` from the listed surface or a `direct_domain_validation` accepted outside an explicitly incomplete frontier.

`parse_action_trace(...)` still accepts `MTGSim.ActionTrace.v1`; parsed v1 rows are treated as source-wildcarded because older artifacts did not record validation provenance. New v2 rows can drive `ChoiceValidationSourceMismatch` replay failures before mutation when the selected-action source drifts.


## rev0099 v3 extension

`serialize_action_trace(...)` now emits `MTGSim.ActionTrace.v3`. v3 keeps the v2 validation-source fields and adds deterministic page-location fields such as `choice_page_found=`, `choice_page_cursor=`, `choice_action_cursor=`, and `choice_page_index=`. `parse_action_trace(...)` remains backward-compatible with v1 and v2; those older formats do not carry page-location evidence and therefore replay treats the page proof as absent rather than false.


## rev0100 v4 extension

`serialize_action_trace(...)` now emits `MTGSim.ActionTrace.v4`. v4 keeps the v3 page-location fields and adds `choice_page_hash=` so replay can bind a selected action to the content of the deterministic page, not only to a cursor/index tuple. `parse_action_trace(...)` remains backward-compatible with `MTGSim.ActionTrace.v1`, `MTGSim.ActionTrace.v2`, and `MTGSim.ActionTrace.v3`; v3 traces do not carry `choice_page_hash` and therefore use a hash wildcard while still checking the older page-location fields.


## rev0102 trace schema note

`serialize_action_trace(...)` now emits `MTGSim.ActionTrace.v5`. v5 keeps the v4 `choice_page_hash=` field and adds `choice_page_schema=` so replay can bind a selected action to both the deterministic page contents and the legal-action page protocol version that produced them. `parse_action_trace(...)` remains backward-compatible with `MTGSim.ActionTrace.v1`, `MTGSim.ActionTrace.v2`, `MTGSim.ActionTrace.v3`, and `MTGSim.ActionTrace.v4`; v4 traces keep page-hash evidence but are schema-wildcarded because they predate `choice_page_schema=`.


## rev0103 trace schema note

`serialize_action_trace(...)` now emits `MTGSim.ActionTrace.v7`. v6 kept the v5 `choice_page_schema=` and `choice_page_hash=` fields and added the page count contract: `choice_page_total_lower=`, `choice_page_total_exact=`, and `choice_page_remaining_lower=`. v7 adds page context evidence: `choice_page_state=` and `choice_page_request_hash=`. `parse_action_trace(...)` remains backward-compatible with `MTGSim.ActionTrace.v1` through `MTGSim.ActionTrace.v6`; v5 traces keep page schema/hash evidence but are count-wildcarded, and pre-v7 traces are context-wildcarded because they predate the page context seal.


## rev0106 trace proof-status note

`serialize_action_trace(...)` now emits `MTGSim.ActionTrace.v8`. v8 keeps the v7 page context fields and adds `choice_page_checked=` so the trace distinguishes a positive located-page claim from the absence of a checked page proof. `parse_action_trace(...)` remains backward-compatible with `MTGSim.ActionTrace.v1` through `MTGSim.ActionTrace.v7`; older page-location traces infer checked status from `choice_page_found=1`, while v8 rejects applied rows that try to carry page fields without a checked page proof.

## Current extension through rev0108

The text codec has been extended through `MTGSim.ActionTrace.v12`. Version 9 added `choice_page_location_hash=`, the compact `LegalActionPageLocation.v1` seal over page-location fields plus the selected action hash. Version 10 added `choice_queue_location_hash=`, the compact `ChoiceQueueLocation.v1` seal over APNAP queue position, selected request metadata, and the selected action hash. Version 11 adds `choice_queue_found=` and `choice_queue_checked=` so APNAP queue proof checking is explicit instead of inferred from a nonzero hash. Version 12 adds `choice_queue_schema=` so the APNAP queue-location proof protocol version is visible outside the compact hash. Older versions remain parseable for historical replay artifacts.


## rev0110 trace schema note

`serialize_action_trace(...)` now emits `MTGSim.ActionTrace.v13`. v13 keeps all v12 page and APNAP queue proof fields and adds `action_schema=` so the canonical selected-action protocol version is visible beside `action_hash=`. `parse_action_trace(...)` remains backward-compatible with `MTGSim.ActionTrace.v1` through `MTGSim.ActionTrace.v12`; older rows default action schema to the current `kLegalActionSchemaVersion` when they carry action-hash evidence, while v13 requires a nonzero `action_schema=` field.

## rev0111 trace v14 choice request schema evidence

`serialize_action_trace(...)` now emits `MTGSim.ActionTrace.v14`. v14 keeps the v13 selected-action `action_schema=` field and adds `choice_schema=` so the local `ChoiceRequest` protocol version is visible beside `choice_hash=`. `parse_action_trace(...)` remains backward-compatible with `MTGSim.ActionTrace.v1` through `MTGSim.ActionTrace.v13`; older rows default choice request schema to the current `kChoiceRequestSchemaVersion` when they carry choice-hash evidence, while v14 requires a nonzero `choice_schema=` field.


## rev0112 trace v15 choice queue schema evidence

`serialize_action_trace(...)` now emits `MTGSim.ActionTrace.v15`. v15 keeps the v14 local `choice_schema=` field and adds `choice_queue_schema=` for the global APNAP `ChoiceRequestQueue` protocol version. Because v12-v14 already used `choice_queue_schema=` for queue-location schema evidence, v15 also emits the queue-location protocol as `choice_queue_location_schema=`.

`parse_action_trace(...)` remains backward-compatible with `MTGSim.ActionTrace.v1` through `MTGSim.ActionTrace.v14`; historical v12-v14 rows keep interpreting legacy `choice_queue_schema=` as queue-location schema evidence, while v15 requires a nonzero global `choice_queue_schema=` when queue evidence is present and reads queue-location schema from `choice_queue_location_schema=`.

## rev0113 trace v16 StateCore hash schema evidence

`serialize_action_trace(...)` now emits `MTGSim.ActionTrace.v16`. v16 keeps the v15 APNAP queue schema fields and adds `state_schema=` so the StateCore hash protocol version is visible beside `state_before=` and `state_after=`.

`parse_action_trace(...)` remains backward-compatible with `MTGSim.ActionTrace.v1` through `MTGSim.ActionTrace.v15`; older rows that carry state hashes default to the current `kStateCoreSchemaVersion`, while v16 requires a nonzero `state_schema=` field. Replay rejects state schema drift as `StateHashSchemaMismatch` before StateCore or journal mutation.

## rev0172 trace v17 trigger-order evidence

`serialize_action_trace(...)` now emits `MTGSim.ActionTrace.v17`. v17 keeps the v16 `state_schema=` field and adds `trigger_order=` to each row. The field is `-` for actions that do not carry explicit trigger order and a comma-separated `TriggerRecord` index list for `PutPendingTriggersOnStack` choices.

`parse_action_trace(...)` remains backward-compatible with `MTGSim.ActionTrace.v1` through `MTGSim.ActionTrace.v16`; v17 requires `trigger_order=`, and older versions reject the field so schema drift cannot silently reinterpret an order-bearing row.

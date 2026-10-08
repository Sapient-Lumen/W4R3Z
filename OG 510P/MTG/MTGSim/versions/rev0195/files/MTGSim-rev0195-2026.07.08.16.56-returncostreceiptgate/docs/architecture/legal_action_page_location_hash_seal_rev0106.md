# rev0106 legal-action page-location hash seal

rev0102 through rev0105 made legal-action pages increasingly explicit: schema/version evidence, count evidence, originating StateCore/request context, and the distinction between "page proof was checked" and "the selected action was found on a page." rev0106 adds the next compact proof boundary: a stable hash for the full page-location proof itself.

## Contract

`LegalActionPageLocation.v1` hashes the page-location tuple that proves where an action was offered:

- found flag, page schema version, choice kind, and chooser;
- originating StateCore hash and ChoiceRequest hash;
- requested/effective page limit, page cursor, action cursor, page index, and next cursor;
- actions seen, scanned pages, page completion, exact/lower-bound count evidence, and remaining lower bound;
- page hash; and
- selected legal-action hash.

This makes the proof self-sealing: the selected action, the page position, the request context, and the count/cursor evidence cannot drift independently without changing `choice_page_location_hash`.

## Trace and receipt surfaces

Action receipts now carry `choice_page_location_hash` beside `choice_page_location_checked` and the detailed page-location fields. `ActionTrace.v9` serializes the same compact hash as `choice_page_location_hash=`. Older trace versions remain parseable, but v9 applied actions with checked page proof must carry a non-zero location hash.

## Replay and validation

Replay reconstructs the expected page location from the trace and compares the compact hash against the freshly located action before mutating state. Receipt validation recomputes `legal_action_page_location_hash(...)` from the typed receipt fields and the selected action hash, rejecting stale or partial page-location proof evidence.

The added regression `test_action_trace_replay_detects_choice_page_location_hash_drift_without_mutation` proves that changing the compact hash on an otherwise valid exported trace stops replay before mutation.
